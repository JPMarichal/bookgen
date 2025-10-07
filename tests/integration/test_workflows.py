"""
Integration tests for multi-service interactions
"""
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.models import Biography, Chapter, Source
from src.repositories import BiographyRepository, ChapterRepository, SourceRepository


pytestmark = [pytest.mark.integration, pytest.mark.slow]


class TestBiographyWorkflow:
    """Integration tests for complete biography workflow"""
    
    @pytest.fixture
    def integration_db(self):
        """Create integration test database"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_complete_biography_creation_workflow(self, integration_db):
        """Test complete workflow: biography -> chapters -> sources"""
        # Create repositories
        bio_repo = BiographyRepository(integration_db)
        chapter_repo = ChapterRepository(integration_db)
        source_repo = SourceRepository(integration_db)
        
        # Step 1: Create biography
        biography = Biography(
            character_name="Winston Churchill",
            status="generating",
            total_chapters=8
        )
        integration_db.add(biography)
        integration_db.commit()
        integration_db.refresh(biography)
        
        assert biography.id is not None
        assert biography.character_name == "Winston Churchill"
        
        # Step 2: Create chapters
        for i in range(1, 9):
            chapter = Chapter(
                biography_id=biography.id,
                number=i,
                title=f"Chapter {i}",
                content=f"Content for chapter {i}",
                word_count=500
            )
            integration_db.add(chapter)
        
        integration_db.commit()
        integration_db.refresh(biography)
        
        assert len(biography.chapters) == 8
        
        # Step 3: Create sources
        for i in range(5):
            source = Source(
                biography_id=biography.id,
                title=f"Source {i}",
                url=f"https://example.com/source{i}",
                source_type="article",
                relevance_score=0.8 + (i * 0.02),
                credibility_score=0.9
            )
            integration_db.add(source)
        
        integration_db.commit()
        integration_db.refresh(biography)
        
        assert len(biography.sources) == 5
        
        # Step 4: Update biography status
        biography.status = "completed"
        integration_db.commit()
        
        # Verify final state
        assert biography.status == "completed"
        assert len(biography.chapters) == 8
        assert len(biography.sources) == 5
    
    def test_biography_with_validation_workflow(self, integration_db):
        """Test biography workflow with validation steps"""
        biography = Biography(
            character_name="Marie Curie",
            status="pending"
        )
        integration_db.add(biography)
        integration_db.commit()
        
        # Add chapter
        chapter = Chapter(
            biography_id=biography.id,
            number=1,
            title="Early Life",
            content=" ".join(["word"] * 2550),  # Exactly 2550 words
            word_count=2550
        )
        integration_db.add(chapter)
        integration_db.commit()
        
        # Validate chapter length
        assert chapter.word_count == 2550
        
        # Update status after validation
        biography.status = "validated"
        integration_db.commit()
        
        assert biography.status == "validated"


class TestServiceIntegration:
    """Integration tests for service interactions"""
    
    @patch('src.services.openrouter_client.requests.post')
    def test_openrouter_with_source_validation(self, mock_post):
        """Test OpenRouter client integration with source validation"""
        from src.services.openrouter_client import OpenRouterClient
        from src.services.source_validator import SourceValidationService
        
        # Mock OpenRouter response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated text"}}]
        }
        mock_post.return_value = mock_response
        
        # Create client
        client = OpenRouterClient()
        
        # Generate content (mocked)
        result = client.generate_text("Test prompt")
        assert result is not None
        
        # Validate sources
        validator = SourceValidationService()
        sources = [
            {
                "title": "Test Source",
                "url": "https://example.edu/article",
                "source_type": "article"
            }
        ]
        
        validation_result = validator.validate_sources(sources, "Test Topic")
        assert validation_result is not None
    
    def test_length_validation_with_concatenation(self):
        """Test length validator integration with concatenation service"""
        from src.services.length_validator import LengthValidationService
        from src.services.concatenation import ConcatenationService
        
        # Create services
        length_validator = LengthValidationService()
        concatenation_service = ConcatenationService()
        
        # Create test chapters
        chapters = [
            {
                "number": 1,
                "title": "Chapter 1",
                "content": " ".join(["word"] * 2550)
            },
            {
                "number": 2,
                "title": "Chapter 2",
                "content": " ".join(["word"] * 2550)
            }
        ]
        
        # Validate each chapter
        for chapter in chapters:
            result = length_validator.validate_chapter(chapter["content"])
            assert result["is_valid"] is True
        
        # Concatenate chapters
        concatenated = concatenation_service.concatenate_chapters(chapters)
        assert concatenated is not None
        assert "content" in concatenated or isinstance(concatenated, str)


class TestDatabaseRepositoryIntegration:
    """Integration tests for database repositories"""
    
    @pytest.fixture
    def repo_db(self):
        """Create repository test database"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_biography_chapter_relationship(self, repo_db):
        """Test biography and chapter repository relationship"""
        bio_repo = BiographyRepository(repo_db)
        chapter_repo = ChapterRepository(repo_db)
        
        # Create biography
        biography = Biography(character_name="Test Character")
        repo_db.add(biography)
        repo_db.commit()
        repo_db.refresh(biography)
        
        # Create chapters through repository
        for i in range(1, 4):
            chapter = Chapter(
                biography_id=biography.id,
                number=i,
                title=f"Chapter {i}",
                word_count=500
            )
            repo_db.add(chapter)
        
        repo_db.commit()
        
        # Query through repository
        chapters = chapter_repo.get_by_biography(biography.id)
        assert len(chapters) == 3
        
        # Verify relationship
        retrieved_bio = bio_repo.get_by_id(biography.id)
        assert len(retrieved_bio.chapters) == 3
    
    def test_source_repository_filtering(self, repo_db):
        """Test source repository filtering capabilities"""
        source_repo = SourceRepository(repo_db)
        
        # Create biography
        biography = Biography(character_name="Test")
        repo_db.add(biography)
        repo_db.commit()
        
        # Create sources with different scores
        sources_data = [
            {"relevance": 0.95, "credibility": 0.98},
            {"relevance": 0.75, "credibility": 0.85},
            {"relevance": 0.60, "credibility": 0.70},
        ]
        
        for idx, data in enumerate(sources_data):
            source = Source(
                biography_id=biography.id,
                title=f"Source {idx}",
                url=f"https://example.com/{idx}",
                source_type="article",
                relevance_score=data["relevance"],
                credibility_score=data["credibility"]
            )
            repo_db.add(source)
        
        repo_db.commit()
        
        # Filter by relevance threshold
        high_relevance = source_repo.get_by_relevance_threshold(0.8)
        assert len(high_relevance) >= 1
        
        for source in high_relevance:
            assert source.relevance_score >= 0.8


class TestEndToEndWorkflow:
    """End-to-end integration tests"""
    
    @pytest.fixture
    def e2e_db(self):
        """Create end-to-end test database"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_full_biography_generation_simulation(self, e2e_db):
        """Simulate full biography generation workflow"""
        # 1. Create initial biography request
        biography = Biography(
            character_name="Albert Einstein",
            status="pending",
            total_chapters=5
        )
        e2e_db.add(biography)
        e2e_db.commit()
        e2e_db.refresh(biography)
        
        # 2. Simulate chapter generation
        biography.status = "generating"
        e2e_db.commit()
        
        for i in range(1, 6):
            chapter = Chapter(
                biography_id=biography.id,
                number=i,
                title=f"Chapter {i}",
                content=" ".join(["word"] * 2550),
                word_count=2550
            )
            e2e_db.add(chapter)
        
        e2e_db.commit()
        
        # 3. Simulate source collection
        for i in range(10):
            source = Source(
                biography_id=biography.id,
                title=f"Einstein Source {i}",
                url=f"https://physics.edu/einstein/{i}",
                source_type="article" if i % 2 == 0 else "book",
                relevance_score=0.85 + (i * 0.01),
                credibility_score=0.90
            )
            e2e_db.add(source)
        
        e2e_db.commit()
        
        # 4. Simulate validation
        biography.status = "validating"
        e2e_db.commit()
        
        # Validate all chapters have correct length
        for chapter in biography.chapters:
            assert chapter.word_count == 2550
        
        # 5. Mark as completed
        biography.status = "completed"
        e2e_db.commit()
        
        # 6. Verify final state
        e2e_db.refresh(biography)
        assert biography.status == "completed"
        assert len(biography.chapters) == 5
        assert len(biography.sources) == 10
        
        # Calculate total words
        total_words = sum(ch.word_count for ch in biography.chapters)
        assert total_words == 12750  # 5 * 2550
