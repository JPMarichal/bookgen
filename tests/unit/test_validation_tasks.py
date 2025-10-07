"""
Unit tests for validation tasks
"""
import pytest
from unittest.mock import patch, MagicMock
from src.tasks.validation_tasks import (
    ValidationTask,
    validate_chapter_length,
    validate_sources,
    validate_content_quality
)


pytestmark = [pytest.mark.unit, pytest.mark.mock]


class TestValidationTask:
    """Test ValidationTask base class"""
    
    def test_validation_task_configuration(self):
        """Test ValidationTask base configuration"""
        task = ValidationTask()
        assert task.autoretry_for == (Exception,)
        assert task.retry_kwargs == {'max_retries': 3}
        assert task.retry_backoff is True
        assert task.retry_backoff_max == 300
        assert task.retry_jitter is True
    
    def test_on_failure_logging(self):
        """Test on_failure method logs errors"""
        task = ValidationTask()
        exc = Exception("Validation error")
        task_id = "val-task-123"
        
        with patch('src.tasks.validation_tasks.logger') as mock_logger:
            task.on_failure(exc, task_id, [], {}, None)
            mock_logger.error.assert_called_once()


class TestValidateChapterLength:
    """Test validate_chapter_length task"""
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_chapter_length_valid(self, mock_logger):
        """Test validation of chapter within acceptable length"""
        content = " ".join(["word"] * 2550)  # Exact target
        
        mock_self = MagicMock()
        mock_self.request.id = "val-123"
        
        result = validate_chapter_length(mock_self, content)
        
        assert result['is_valid'] is True
        assert result['actual_length'] == 2550
        assert result['target_length'] == 2550
        assert result['deviation_percent'] == 0.0
        assert result['quality_score'] == 100
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_chapter_length_too_short(self, mock_logger):
        """Test validation of chapter that's too short"""
        content = " ".join(["word"] * 2000)  # Below minimum
        
        mock_self = MagicMock()
        mock_self.request.id = "val-124"
        
        result = validate_chapter_length(mock_self, content)
        
        assert result['is_valid'] is False
        assert result['actual_length'] == 2000
        assert result['deviation_percent'] < 0
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_chapter_length_too_long(self, mock_logger):
        """Test validation of chapter that's too long"""
        content = " ".join(["word"] * 3000)  # Above maximum
        
        mock_self = MagicMock()
        mock_self.request.id = "val-125"
        
        result = validate_chapter_length(mock_self, content)
        
        assert result['is_valid'] is False
        assert result['actual_length'] == 3000
        assert result['deviation_percent'] > 0
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_chapter_length_custom_tolerance(self, mock_logger):
        """Test validation with custom tolerance"""
        content = " ".join(["word"] * 2700)  # 5.9% over
        
        mock_self = MagicMock()
        mock_self.request.id = "val-126"
        
        # Should fail with 5% tolerance
        result = validate_chapter_length(mock_self, content, 2550, 0.05)
        assert result['is_valid'] is False
        
        # Should pass with 10% tolerance
        result = validate_chapter_length(mock_self, content, 2550, 0.10)
        assert result['is_valid'] is True
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_chapter_length_edge_cases(self, mock_logger):
        """Test validation edge cases"""
        mock_self = MagicMock()
        mock_self.request.id = "val-127"
        
        # Empty content
        result = validate_chapter_length(mock_self, "")
        assert result['actual_length'] == 0
        assert result['is_valid'] is False
        
        # Single word
        result = validate_chapter_length(mock_self, "word")
        assert result['actual_length'] == 1
        assert result['is_valid'] is False


class TestValidateSources:
    """Test validate_sources task"""
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_sources_valid(self, mock_logger):
        """Test validation of valid sources"""
        sources = [
            {
                "title": "Source 1",
                "url": "https://britannica.com/article",
                "relevance_score": 0.9,
                "credibility_score": 0.95
            },
            {
                "title": "Source 2",
                "url": "https://edu.org/article",
                "relevance_score": 0.85,
                "credibility_score": 0.90
            }
        ]
        
        mock_self = MagicMock()
        mock_self.request.id = "src-val-123"
        
        result = validate_sources(mock_self, sources)
        
        assert result['is_valid'] is True
        assert result['total_sources'] == 2
        assert 'task_id' in result
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_sources_insufficient(self, mock_logger):
        """Test validation with insufficient sources"""
        sources = [{"title": "Only One", "url": "https://test.com"}]
        
        mock_self = MagicMock()
        mock_self.request.id = "src-val-124"
        
        result = validate_sources(mock_self, sources, min_sources=3)
        
        assert result['is_valid'] is False
        assert result['total_sources'] == 1
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_sources_low_quality(self, mock_logger):
        """Test validation with low quality sources"""
        sources = [
            {
                "title": "Low Quality",
                "url": "https://random.com",
                "relevance_score": 0.3,
                "credibility_score": 0.4
            }
        ]
        
        mock_self = MagicMock()
        mock_self.request.id = "src-val-125"
        
        result = validate_sources(mock_self, sources)
        
        # Result structure should be returned
        assert 'is_valid' in result
        assert 'total_sources' in result
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_sources_empty(self, mock_logger):
        """Test validation with empty source list"""
        mock_self = MagicMock()
        mock_self.request.id = "src-val-126"
        
        result = validate_sources(mock_self, [])
        
        assert result['is_valid'] is False
        assert result['total_sources'] == 0


class TestValidateContentQuality:
    """Test validate_content_quality task"""
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_content_quality_high(self, mock_logger):
        """Test validation of high-quality content"""
        content = """
        This is a well-written biographical chapter with proper structure.
        It contains multiple paragraphs, varied sentence structures, and 
        comprehensive information about the subject. The narrative flows 
        naturally and maintains reader engagement throughout. Historical 
        facts are presented accurately with appropriate context.
        """ * 10  # Make it longer
        
        mock_self = MagicMock()
        mock_self.request.id = "qual-123"
        
        result = validate_content_quality(mock_self, content)
        
        assert result['is_valid'] is True
        assert 'quality_score' in result
        assert result['quality_score'] > 0
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_content_quality_low(self, mock_logger):
        """Test validation of low-quality content"""
        content = "Short. Bad. Quality."
        
        mock_self = MagicMock()
        mock_self.request.id = "qual-124"
        
        result = validate_content_quality(mock_self, content)
        
        assert 'is_valid' in result
        assert 'quality_score' in result
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_content_quality_metrics(self, mock_logger):
        """Test quality validation includes all required metrics"""
        content = "This is a test chapter with some content. " * 50
        
        mock_self = MagicMock()
        mock_self.request.id = "qual-125"
        
        result = validate_content_quality(mock_self, content)
        
        assert 'is_valid' in result
        assert 'quality_score' in result
        assert 'task_id' in result
    
    @patch('src.tasks.validation_tasks.logger')
    def test_validate_content_quality_empty(self, mock_logger):
        """Test validation of empty content"""
        mock_self = MagicMock()
        mock_self.request.id = "qual-126"
        
        result = validate_content_quality(mock_self, "")
        
        assert result['is_valid'] is False


class TestValidationTasksIntegration:
    """Integration tests for validation tasks"""
    
    @pytest.mark.integration
    @patch('src.tasks.validation_tasks.logger')
    def test_complete_validation_workflow(self, mock_logger):
        """Test complete validation workflow"""
        content = " ".join(["word"] * 2550)
        sources = [
            {"title": "Source", "url": "https://test.edu", "relevance_score": 0.9}
        ]
        
        mock_self = MagicMock()
        
        # Validate length
        mock_self.request.id = "workflow-1"
        length_result = validate_chapter_length(mock_self, content)
        assert length_result['is_valid'] is True
        
        # Validate sources
        mock_self.request.id = "workflow-2"
        source_result = validate_sources(mock_self, sources)
        assert 'is_valid' in source_result
        
        # Validate quality
        mock_self.request.id = "workflow-3"
        quality_result = validate_content_quality(mock_self, content)
        assert 'is_valid' in quality_result
