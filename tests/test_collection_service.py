"""
Tests for collection service
"""
import pytest
import os
import tempfile
from pathlib import Path

from src.services.collection_service import CollectionService


class TestCollectionService:
    """Tests for CollectionService"""
    
    @pytest.fixture
    def temp_collections_dir(self):
        """Create a temporary collections directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_collection_file(self, temp_collections_dir):
        """Create a sample collection file"""
        collection_content = """1.1. Joseph Stalin ✅
2.2. Harry S. Truman ✅
3.3. Winston Churchill ✅
4.4. Dwight D. Eisenhower
5.5. Nikita Khrushchev
6.6. John F. Kennedy
7.7. Lyndon B. Johnson
"""
        collection_path = os.path.join(temp_collections_dir, "test_collection.md")
        with open(collection_path, 'w', encoding='utf-8') as f:
            f.write(collection_content)
        return "test_collection.md"
    
    def test_find_first_uncompleted(self, temp_collections_dir, sample_collection_file):
        """Test finding first uncompleted character"""
        service = CollectionService(collections_base_path=temp_collections_dir)
        
        line_idx, line_number, character_name = service.find_first_uncompleted(sample_collection_file)
        
        assert line_idx == 3
        assert line_number == "4.4. "
        assert character_name == "Dwight D. Eisenhower"
    
    def test_find_first_uncompleted_all_completed(self, temp_collections_dir):
        """Test when all characters are completed"""
        collection_content = """1. Character One ✅
2. Character Two ✅
3. Character Three ✅
"""
        collection_path = os.path.join(temp_collections_dir, "all_completed.md")
        with open(collection_path, 'w', encoding='utf-8') as f:
            f.write(collection_content)
        
        service = CollectionService(collections_base_path=temp_collections_dir)
        line_idx, line_number, character_name = service.find_first_uncompleted("all_completed.md")
        
        assert line_idx is None
        assert line_number is None
        assert character_name is None
    
    def test_find_first_uncompleted_file_not_found(self, temp_collections_dir):
        """Test with non-existent file"""
        service = CollectionService(collections_base_path=temp_collections_dir)
        
        with pytest.raises(FileNotFoundError):
            service.find_first_uncompleted("nonexistent.md")
    
    def test_mark_as_completed(self, temp_collections_dir, sample_collection_file):
        """Test marking a character as completed"""
        service = CollectionService(collections_base_path=temp_collections_dir)
        
        # Mark a character as completed
        result = service.mark_as_completed(sample_collection_file, "Dwight D. Eisenhower")
        assert result is True
        
        # Verify it was marked
        collection_path = os.path.join(temp_collections_dir, sample_collection_file)
        with open(collection_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "4.4. Dwight D. Eisenhower ✅" in content
    
    def test_mark_as_completed_not_found(self, temp_collections_dir, sample_collection_file):
        """Test marking a non-existent character"""
        service = CollectionService(collections_base_path=temp_collections_dir)
        
        result = service.mark_as_completed(sample_collection_file, "Non Existent Character")
        assert result is False
    
    def test_list_collections(self, temp_collections_dir):
        """Test listing collection files"""
        # Create multiple collection files
        for i in range(3):
            filepath = os.path.join(temp_collections_dir, f"collection_{i}.md")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Collection {i}\n")
        
        # Create a non-.md file (should be ignored)
        with open(os.path.join(temp_collections_dir, "not_a_collection.txt"), 'w') as f:
            f.write("Not a collection\n")
        
        service = CollectionService(collections_base_path=temp_collections_dir)
        collections = service.list_collections()
        
        assert len(collections) == 3
        assert "collection_0.md" in collections
        assert "collection_1.md" in collections
        assert "collection_2.md" in collections
        assert "not_a_collection.txt" not in collections
    
    def test_get_collection_stats(self, temp_collections_dir, sample_collection_file):
        """Test getting collection statistics"""
        service = CollectionService(collections_base_path=temp_collections_dir)
        
        stats = service.get_collection_stats(sample_collection_file)
        
        assert stats['collection_file'] == sample_collection_file
        assert stats['total_characters'] == 7
        assert stats['completed'] == 3
        assert stats['remaining'] == 4
        assert stats['completion_percentage'] == pytest.approx(42.86, rel=0.1)
    
    def test_normalize_character_name(self):
        """Test character name normalization"""
        # Test basic normalization
        assert CollectionService.normalize_character_name("John F. Kennedy") == "john_f_kennedy"
        
        # Test with special characters
        assert CollectionService.normalize_character_name("Ernesto \"Che\" Guevara") == "ernesto_che_guevara"
        
        # Test with parentheses
        assert CollectionService.normalize_character_name("Karol Wojtyla (Papa Juan Pablo II)") == "karol_wojtyla_papa_juan_pablo_ii"
        
        # Test with multiple spaces
        assert CollectionService.normalize_character_name("George  H.  W.  Bush") == "george_h_w_bush"
        
        # Test lowercase
        assert CollectionService.normalize_character_name("WINSTON CHURCHILL") == "winston_churchill"
    
    def test_get_collection_path_absolute(self, temp_collections_dir):
        """Test get_collection_path with absolute path"""
        service = CollectionService(collections_base_path=temp_collections_dir)
        
        absolute_path = "/absolute/path/to/collection.md"
        result = service._get_collection_path(absolute_path)
        
        assert result == absolute_path
    
    def test_get_collection_path_relative(self, temp_collections_dir):
        """Test get_collection_path with relative path"""
        service = CollectionService(collections_base_path=temp_collections_dir)
        
        relative_path = "collection.md"
        result = service._get_collection_path(relative_path)
        
        assert result == os.path.join(temp_collections_dir, relative_path)
    
    def test_find_uncompleted_without_numbering(self, temp_collections_dir):
        """Test finding uncompleted character without line numbering"""
        collection_content = """Joseph Stalin ✅
Harry S. Truman ✅
Winston Churchill
Dwight D. Eisenhower
"""
        collection_path = os.path.join(temp_collections_dir, "no_numbers.md")
        with open(collection_path, 'w', encoding='utf-8') as f:
            f.write(collection_content)
        
        service = CollectionService(collections_base_path=temp_collections_dir)
        line_idx, line_number, character_name = service.find_first_uncompleted("no_numbers.md")
        
        assert line_idx == 2
        assert line_number == ""
        assert character_name == "Winston Churchill"
