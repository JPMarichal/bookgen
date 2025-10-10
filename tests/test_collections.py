"""
Tests for collection-based biography generation endpoints
"""
import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.main import app

client = TestClient(app)


class TestCollectionEndpoints:
    """Tests for collection endpoints"""
    
    @pytest.fixture
    def temp_collections_dir(self):
        """Create a temporary collections directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def mock_collection_file(self, temp_collections_dir):
        """Create a mock collection file"""
        collection_content = """1. Joseph Stalin ✅
2. Harry S. Truman ✅
3. Winston Churchill ✅
4. Dwight D. Eisenhower
5. Nikita Khrushchev
"""
        collection_path = os.path.join(temp_collections_dir, "test_collection.md")
        with open(collection_path, 'w', encoding='utf-8') as f:
            f.write(collection_content)
        return temp_collections_dir, "test_collection.md"
    
    def test_generate_next_from_collection(self, mock_collection_file):
        """Test generating biography from collection"""
        temp_dir, collection_file = mock_collection_file
        
        # Patch the collection service to use temp directory
        with patch('src.api.routers.collections.collection_service') as mock_service:
            from src.services.collection_service import CollectionService
            
            # Use real service with temp directory
            real_service = CollectionService(collections_base_path=temp_dir)
            mock_service.find_first_uncompleted = real_service.find_first_uncompleted
            mock_service.mark_as_completed = real_service.mark_as_completed
            mock_service.normalize_character_name = CollectionService.normalize_character_name
            
            # Mock the generate_biography function to avoid actual generation
            with patch('src.api.routers.collections.generate_biography') as mock_generate:
                from src.api.models.biographies import BiographyGenerateResponse, JobStatus, GenerationMode
                from datetime import datetime, timezone
                
                # Mock response from generate_biography
                mock_generate.return_value = BiographyGenerateResponse(
                    job_id="test-job-id",
                    status=JobStatus.PENDING,
                    message="Test job created",
                    character="Dwight D. Eisenhower",
                    chapters=20,
                    created_at=datetime.now(timezone.utc),
                    estimated_completion_time="600 seconds",
                    mode=GenerationMode.AUTOMATIC,
                    sources_generated_automatically=True,
                    source_count=40
                )
                
                response = client.post(
                    "/api/v1/collections/generate-next",
                    json={
                        "collection_file": collection_file,
                        "mode": "automatic",
                        "chapters": 20,
                        "mark_completed": False
                    }
                )
                
                assert response.status_code == 202
                data = response.json()
                
                assert "job_id" in data
                assert data["character"] == "Dwight D. Eisenhower"
                assert data["character_normalized"] == "dwight_d_eisenhower"
                assert data["collection_file"] == collection_file
                assert data["status"] == "pending"
    
    def test_generate_next_all_completed(self, temp_collections_dir):
        """Test when all characters are completed"""
        # Create collection with all completed
        collection_content = """1. Character One ✅
2. Character Two ✅
"""
        collection_path = os.path.join(temp_collections_dir, "all_done.md")
        with open(collection_path, 'w', encoding='utf-8') as f:
            f.write(collection_content)
        
        with patch('src.api.routers.collections.collection_service') as mock_service:
            from src.services.collection_service import CollectionService
            
            real_service = CollectionService(collections_base_path=temp_collections_dir)
            mock_service.find_first_uncompleted = real_service.find_first_uncompleted
            
            response = client.post(
                "/api/v1/collections/generate-next",
                json={
                    "collection_file": "all_done.md",
                    "mode": "automatic"
                }
            )
            
            assert response.status_code == 404
            assert "No uncompleted characters" in response.json()["detail"]
    
    def test_generate_next_file_not_found(self):
        """Test with non-existent collection file"""
        response = client.post(
            "/api/v1/collections/generate-next",
            json={
                "collection_file": "nonexistent.md",
                "mode": "automatic"
            }
        )
        
        assert response.status_code == 404
    
    def test_get_collection_stats(self, mock_collection_file):
        """Test getting collection statistics"""
        temp_dir, collection_file = mock_collection_file
        
        with patch('src.api.routers.collections.collection_service') as mock_service:
            from src.services.collection_service import CollectionService
            
            real_service = CollectionService(collections_base_path=temp_dir)
            mock_service.get_collection_stats = real_service.get_collection_stats
            
            response = client.get(f"/api/v1/collections/{collection_file}/stats")
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["collection_file"] == collection_file
            assert data["total_characters"] == 5
            assert data["completed"] == 3
            assert data["remaining"] == 2
            assert "completion_percentage" in data
    
    def test_get_collection_stats_file_not_found(self):
        """Test getting stats for non-existent file"""
        response = client.get("/api/v1/collections/nonexistent.md/stats")
        
        assert response.status_code == 404
    
    def test_list_collections(self, temp_collections_dir):
        """Test listing all collections"""
        # Create some collection files
        for i in range(3):
            filepath = os.path.join(temp_collections_dir, f"collection_{i}.md")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Collection {i}\n")
        
        with patch('src.api.routers.collections.collection_service') as mock_service:
            from src.services.collection_service import CollectionService
            
            real_service = CollectionService(collections_base_path=temp_collections_dir)
            mock_service.list_collections = real_service.list_collections
            
            response = client.get("/api/v1/collections/")
            
            assert response.status_code == 200
            data = response.json()
            
            assert "collections" in data
            assert "count" in data
            assert data["count"] == 3
    
    def test_generate_next_with_mark_completed(self, mock_collection_file):
        """Test that mark_completed flag works"""
        temp_dir, collection_file = mock_collection_file
        
        with patch('src.api.routers.collections.collection_service') as mock_service:
            from src.services.collection_service import CollectionService
            
            real_service = CollectionService(collections_base_path=temp_dir)
            mock_service.find_first_uncompleted = real_service.find_first_uncompleted
            mock_service.mark_as_completed = real_service.mark_as_completed
            mock_service.normalize_character_name = CollectionService.normalize_character_name
            
            # Mock the generate_biography function
            with patch('src.api.routers.collections.generate_biography') as mock_generate:
                from src.api.models.biographies import BiographyGenerateResponse, JobStatus, GenerationMode
                from datetime import datetime, timezone
                
                mock_generate.return_value = BiographyGenerateResponse(
                    job_id="test-job-id",
                    status=JobStatus.PENDING,
                    message="Test job created",
                    character="Dwight D. Eisenhower",
                    chapters=20,
                    created_at=datetime.now(timezone.utc),
                    estimated_completion_time="600 seconds",
                    mode=GenerationMode.AUTOMATIC,
                    sources_generated_automatically=True,
                    source_count=40
                )
                
                response = client.post(
                    "/api/v1/collections/generate-next",
                    json={
                        "collection_file": collection_file,
                        "mode": "automatic",
                        "mark_completed": True
                    }
                )
                
                assert response.status_code == 202
                
                # Verify character was marked
                collection_path = os.path.join(temp_dir, collection_file)
                with open(collection_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                assert "Dwight D. Eisenhower ✅" in content
    
    def test_generate_next_with_custom_parameters(self, mock_collection_file):
        """Test with custom generation parameters"""
        temp_dir, collection_file = mock_collection_file
        
        with patch('src.api.routers.collections.collection_service') as mock_service:
            from src.services.collection_service import CollectionService
            
            real_service = CollectionService(collections_base_path=temp_dir)
            mock_service.find_first_uncompleted = real_service.find_first_uncompleted
            mock_service.mark_as_completed = real_service.mark_as_completed
            mock_service.normalize_character_name = CollectionService.normalize_character_name
            
            # Mock the generate_biography function
            with patch('src.api.routers.collections.generate_biography') as mock_generate:
                from src.api.models.biographies import BiographyGenerateResponse, JobStatus, GenerationMode
                from datetime import datetime, timezone
                
                mock_generate.return_value = BiographyGenerateResponse(
                    job_id="test-job-id",
                    status=JobStatus.PENDING,
                    message="Test job created",
                    character="Dwight D. Eisenhower",
                    chapters=15,
                    created_at=datetime.now(timezone.utc),
                    estimated_completion_time="450 seconds",
                    mode=GenerationMode.AUTOMATIC,
                    sources_generated_automatically=True,
                    source_count=30
                )
                
                response = client.post(
                    "/api/v1/collections/generate-next",
                    json={
                        "collection_file": collection_file,
                        "mode": "automatic",
                        "chapters": 15,
                        "total_words": 30000,
                        "min_sources": 30,
                        "quality_threshold": 0.9,
                        "mark_completed": False
                    }
                )
                
                assert response.status_code == 202
                data = response.json()
                
                assert data["chapters"] == 15
                assert data["mode"] == "automatic"
