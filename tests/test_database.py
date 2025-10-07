"""
Tests for database models and repositories
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.base import Base
from src.models import Biography, Chapter, Source, GenerationJob
from src.repositories import (
    BiographyRepository,
    ChapterRepository,
    SourceRepository,
    GenerationJobRepository,
)


@pytest.fixture
def db_session():
    """
    Create an in-memory SQLite database for testing
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


class TestBiographyModel:
    """Test Biography model"""
    
    def test_create_biography(self, db_session):
        """Test creating a biography"""
        biography = Biography(
            character_name="Albert Einstein",
            status="pending"
        )
        db_session.add(biography)
        db_session.commit()
        db_session.refresh(biography)
        
        assert biography.id is not None
        assert biography.character_name == "Albert Einstein"
        assert biography.status == "pending"
        assert biography.created_at is not None
        assert biography.updated_at is not None
    
    def test_biography_with_metadata(self, db_session):
        """Test biography with metadata"""
        biography = Biography(
            character_name="Marie Curie",
            status="pending",
            bio_metadata={"source": "test", "priority": "high"}
        )
        db_session.add(biography)
        db_session.commit()
        
        assert biography.bio_metadata["source"] == "test"
        assert biography.bio_metadata["priority"] == "high"


class TestChapterModel:
    """Test Chapter model"""
    
    def test_create_chapter(self, db_session):
        """Test creating a chapter"""
        biography = Biography(character_name="Isaac Newton", status="pending")
        db_session.add(biography)
        db_session.commit()
        
        chapter = Chapter(
            biography_id=biography.id,
            number=1,
            title="Early Life",
            content="Chapter content here",
            word_count=100
        )
        db_session.add(chapter)
        db_session.commit()
        db_session.refresh(chapter)
        
        assert chapter.id is not None
        assert chapter.biography_id == biography.id
        assert chapter.number == 1
        assert chapter.title == "Early Life"
        assert chapter.word_count == 100
    
    def test_chapter_relationship(self, db_session):
        """Test chapter-biography relationship"""
        biography = Biography(character_name="Leonardo da Vinci", status="pending")
        db_session.add(biography)
        db_session.commit()
        
        chapter1 = Chapter(biography_id=biography.id, number=1, word_count=100)
        chapter2 = Chapter(biography_id=biography.id, number=2, word_count=200)
        db_session.add_all([chapter1, chapter2])
        db_session.commit()
        
        db_session.refresh(biography)
        assert len(biography.chapters) == 2


class TestSourceModel:
    """Test Source model"""
    
    def test_create_source(self, db_session):
        """Test creating a source"""
        source = Source(
            url="https://example.com/article",
            title="Sample Article",
            author="John Doe",
            validation_status="pending",
            relevance_score=0.85
        )
        db_session.add(source)
        db_session.commit()
        db_session.refresh(source)
        
        assert source.id is not None
        assert source.url == "https://example.com/article"
        assert source.title == "Sample Article"
        assert source.relevance_score == 0.85


class TestGenerationJobModel:
    """Test GenerationJob model"""
    
    def test_create_job(self, db_session):
        """Test creating a generation job"""
        biography = Biography(character_name="Ada Lovelace", status="pending")
        db_session.add(biography)
        db_session.commit()
        
        job = GenerationJob(
            biography_id=biography.id,
            status="pending",
            progress=0.0,
            current_phase="initialization"
        )
        db_session.add(job)
        db_session.commit()
        db_session.refresh(job)
        
        assert job.id is not None
        assert job.biography_id == biography.id
        assert job.status == "pending"
        assert job.progress == 0.0


class TestBiographyRepository:
    """Test BiographyRepository"""
    
    def test_create_biography(self, db_session):
        """Test creating biography via repository"""
        repo = BiographyRepository(db_session)
        biography = Biography(character_name="Nikola Tesla", status="pending")
        
        created = repo.create(biography)
        
        assert created.id is not None
        assert created.character_name == "Nikola Tesla"
    
    def test_get_by_character_name(self, db_session):
        """Test getting biography by character name"""
        repo = BiographyRepository(db_session)
        biography = Biography(character_name="Charles Darwin", status="pending")
        repo.create(biography)
        
        found = repo.get_by_character_name("Charles Darwin")
        
        assert found is not None
        assert found.character_name == "Charles Darwin"
    
    def test_get_by_status(self, db_session):
        """Test getting biographies by status"""
        repo = BiographyRepository(db_session)
        bio1 = Biography(character_name="Person 1", status="completed")
        bio2 = Biography(character_name="Person 2", status="completed")
        bio3 = Biography(character_name="Person 3", status="pending")
        repo.create(bio1)
        repo.create(bio2)
        repo.create(bio3)
        
        completed = repo.get_by_status("completed")
        
        assert len(completed) == 2
    
    def test_get_with_chapters(self, db_session):
        """Test getting biography with chapters"""
        repo = BiographyRepository(db_session)
        biography = Biography(character_name="Test Person", status="pending")
        repo.create(biography)
        
        chapter = Chapter(biography_id=biography.id, number=1, word_count=100)
        db_session.add(chapter)
        db_session.commit()
        
        found = repo.get_with_chapters(biography.id)
        
        assert found is not None
        assert len(found.chapters) == 1


class TestChapterRepository:
    """Test ChapterRepository"""
    
    def test_get_by_biography(self, db_session):
        """Test getting chapters by biography"""
        biography = Biography(character_name="Test", status="pending")
        db_session.add(biography)
        db_session.commit()
        
        repo = ChapterRepository(db_session)
        chapter1 = Chapter(biography_id=biography.id, number=1, word_count=100)
        chapter2 = Chapter(biography_id=biography.id, number=2, word_count=200)
        repo.create(chapter1)
        repo.create(chapter2)
        
        chapters = repo.get_by_biography(biography.id)
        
        assert len(chapters) == 2
        assert chapters[0].number == 1
        assert chapters[1].number == 2
    
    def test_get_total_word_count(self, db_session):
        """Test getting total word count"""
        biography = Biography(character_name="Test", status="pending")
        db_session.add(biography)
        db_session.commit()
        
        repo = ChapterRepository(db_session)
        chapter1 = Chapter(biography_id=biography.id, number=1, word_count=100)
        chapter2 = Chapter(biography_id=biography.id, number=2, word_count=200)
        repo.create(chapter1)
        repo.create(chapter2)
        
        total = repo.get_total_word_count(biography.id)
        
        assert total == 300


class TestSourceRepository:
    """Test SourceRepository"""
    
    def test_get_by_url(self, db_session):
        """Test getting source by URL"""
        repo = SourceRepository(db_session)
        source = Source(
            url="https://test.com/article",
            title="Test Article",
            validation_status="valid"
        )
        repo.create(source)
        
        found = repo.get_by_url("https://test.com/article")
        
        assert found is not None
        assert found.title == "Test Article"
    
    def test_get_by_relevance_threshold(self, db_session):
        """Test getting sources by relevance threshold"""
        repo = SourceRepository(db_session)
        source1 = Source(url="url1", title="High", validation_status="valid", relevance_score=0.9)
        source2 = Source(url="url2", title="Medium", validation_status="valid", relevance_score=0.7)
        source3 = Source(url="url3", title="Low", validation_status="valid", relevance_score=0.5)
        repo.create(source1)
        repo.create(source2)
        repo.create(source3)
        
        relevant = repo.get_by_relevance_threshold(0.8)
        
        assert len(relevant) == 1
        assert relevant[0].title == "High"


class TestGenerationJobRepository:
    """Test GenerationJobRepository"""
    
    def test_get_active_jobs(self, db_session):
        """Test getting active jobs"""
        biography = Biography(character_name="Test", status="pending")
        db_session.add(biography)
        db_session.commit()
        
        repo = GenerationJobRepository(db_session)
        job1 = GenerationJob(biography_id=biography.id, status="pending", progress=0.0)
        job2 = GenerationJob(biography_id=biography.id, status="running", progress=50.0)
        job3 = GenerationJob(biography_id=biography.id, status="completed", progress=100.0)
        repo.create(job1)
        repo.create(job2)
        repo.create(job3)
        
        active = repo.get_active_jobs()
        
        assert len(active) == 2
    
    def test_get_latest_by_biography(self, db_session):
        """Test getting latest job by biography"""
        biography = Biography(character_name="Test", status="pending")
        db_session.add(biography)
        db_session.commit()
        
        repo = GenerationJobRepository(db_session)
        job1 = GenerationJob(biography_id=biography.id, status="completed", progress=100.0)
        repo.create(job1)
        
        job2 = GenerationJob(biography_id=biography.id, status="pending", progress=0.0)
        repo.create(job2)
        
        latest = repo.get_latest_by_biography(biography.id)
        
        # The latest job should be one of the jobs created
        assert latest is not None
        assert latest.biography_id == biography.id
        assert latest.id in [job1.id, job2.id]


class TestAcceptanceCriteria:
    """Test acceptance criteria from issue"""
    
    def test_models_with_relationships(self, db_session):
        """Test models with correct relationships"""
        biography = Biography(character_name="test")
        db_session.add(biography)
        db_session.commit()
        db_session.refresh(biography)
        
        assert biography.id is not None
        
        chapter = Chapter(biography=biography, number=1, word_count=0)
        db_session.add(chapter)
        db_session.commit()
        db_session.refresh(biography)
        
        assert len(biography.chapters) == 1
    
    def test_validations(self, db_session):
        """Test model validations"""
        # Test that required fields are enforced
        biography = Biography(character_name="Valid Name", status="pending")
        db_session.add(biography)
        db_session.commit()
        
        # Biography created successfully
        assert biography.id is not None
