"""
Unit tests for export tasks
"""
import pytest
from unittest.mock import patch, MagicMock
from src.tasks.export_tasks import (
    ExportTask,
    export_to_markdown,
    export_to_word
)


pytestmark = [pytest.mark.unit, pytest.mark.mock]


class TestExportTask:
    """Test ExportTask base class"""
    
    def test_export_task_configuration(self):
        """Test ExportTask base configuration"""
        task = ExportTask()
        assert task.autoretry_for == (Exception,)
        assert task.retry_kwargs == {'max_retries': 3}
        assert task.retry_backoff is True
        assert task.retry_backoff_max == 300
        assert task.retry_jitter is True
    
    def test_on_failure_logging(self):
        """Test on_failure method logs errors"""
        task = ExportTask()
        exc = Exception("Test error")
        task_id = "test-task-123"
        
        with patch('src.tasks.export_tasks.logger') as mock_logger:
            task.on_failure(exc, task_id, [], {}, None)
            mock_logger.error.assert_called_once()


class TestExportToMarkdown:
    """Test export_to_markdown task"""
    
    @patch('src.tasks.export_tasks.logger')
    def test_export_to_markdown_success(self, mock_logger):
        """Test successful markdown export"""
        character_name = "Winston Churchill"
        content = {
            "title": "Biography",
            "chapters": ["Chapter 1", "Chapter 2"]
        }
        
        # Create a mock self with request attribute
        mock_self = MagicMock()
        mock_self.request.id = "task-123"
        
        result = export_to_markdown(mock_self, character_name, content)
        
        assert result['success'] is True
        assert result['character_name'] == character_name
        assert result['format'] == 'markdown'
        assert result['output_path'] == f"/app/bios/{character_name}/biography.md"
        assert 'task_id' in result
        
        # Verify logging
        assert mock_logger.info.call_count >= 1
    
    @patch('src.tasks.export_tasks.logger')
    def test_export_to_markdown_custom_path(self, mock_logger):
        """Test markdown export with custom output path"""
        character_name = "Albert Einstein"
        content = {"chapters": []}
        custom_path = "/custom/path/biography.md"
        
        mock_self = MagicMock()
        mock_self.request.id = "task-456"
        
        result = export_to_markdown(mock_self, character_name, content, custom_path)
        
        assert result['output_path'] == custom_path
    
    @patch('src.tasks.export_tasks.logger')
    def test_export_to_markdown_error_handling(self, mock_logger):
        """Test error handling in markdown export"""
        mock_self = MagicMock()
        mock_self.request.id = "task-789"
        
        # Force an error by making request.id raise an exception
        mock_self.request.id = property(lambda self: (_ for _ in ()).throw(ValueError("Test error")))
        
        with pytest.raises(ValueError):
            export_to_markdown(mock_self, "Test", {})


class TestExportToWord:
    """Test export_to_word task"""
    
    @patch('src.tasks.export_tasks.logger')
    def test_export_to_word_success(self, mock_logger):
        """Test successful Word export"""
        character_name = "Marie Curie"
        content = {
            "title": "Biography",
            "chapters": ["Chapter 1"]
        }
        
        mock_self = MagicMock()
        mock_self.request.id = "task-word-123"
        
        result = export_to_word(mock_self, character_name, content)
        
        assert result['success'] is True
        assert result['character_name'] == character_name
        assert result['format'] == 'docx'
        assert '.docx' in result['output_path']
        assert 'task_id' in result
    
    @patch('src.tasks.export_tasks.logger')
    def test_export_to_word_custom_path(self, mock_logger):
        """Test Word export with custom output path"""
        character_name = "Nikola Tesla"
        content = {"chapters": []}
        custom_path = "/custom/path/biography.docx"
        
        mock_self = MagicMock()
        mock_self.request.id = "task-word-456"
        
        result = export_to_word(mock_self, character_name, content, custom_path)
        
        assert result['output_path'] == custom_path
    
    @patch('src.tasks.export_tasks.logger')
    def test_export_to_word_metadata(self, mock_logger):
        """Test Word export includes metadata"""
        character_name = "Ada Lovelace"
        content = {"title": "Test"}
        
        mock_self = MagicMock()
        mock_self.request.id = "task-word-789"
        
        result = export_to_word(mock_self, character_name, content)
        
        assert result['character_name'] == character_name
        assert result['format'] == 'docx'


class TestExportTaskIntegration:
    """Integration tests for export tasks"""
    
    @pytest.mark.integration
    @patch('src.tasks.export_tasks.logger')
    def test_export_task_chain(self, mock_logger):
        """Test chaining multiple export tasks"""
        character_name = "Leonardo da Vinci"
        content = {"chapters": ["Intro", "Main", "Conclusion"]}
        
        mock_self = MagicMock()
        mock_self.request.id = "chain-task-1"
        
        # Test markdown export
        md_result = export_to_markdown(mock_self, character_name, content)
        assert md_result['success'] is True
        
        # Test word export
        mock_self.request.id = "chain-task-2"
        word_result = export_to_word(mock_self, character_name, content)
        assert word_result['success'] is True
        
        # Both should have the same character name
        assert md_result['character_name'] == word_result['character_name']
