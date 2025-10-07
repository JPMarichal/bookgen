"""
Unit tests for generation tasks
"""
import pytest
from unittest.mock import patch, MagicMock
from src.tasks.generation_tasks import (
    GenerationTask,
    generate_chapter,
    generate_introduction,
    generate_conclusion
)


pytestmark = [pytest.mark.unit, pytest.mark.mock]


class TestGenerationTask:
    """Test GenerationTask base class"""
    
    def test_generation_task_configuration(self):
        """Test GenerationTask base configuration"""
        task = GenerationTask()
        assert task.autoretry_for == (Exception,)
        assert task.retry_kwargs == {'max_retries': 3}
        assert task.retry_backoff is True
        assert task.retry_backoff_max == 600
        assert task.retry_jitter is True
    
    def test_on_failure_logging(self):
        """Test on_failure method logs errors"""
        task = GenerationTask()
        exc = Exception("Generation error")
        task_id = "gen-task-123"
        
        with patch('src.tasks.generation_tasks.logger') as mock_logger:
            task.on_failure(exc, task_id, [], {}, None)
            mock_logger.error.assert_called_once()


class TestGenerateChapter:
    """Test generate_chapter task"""
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_chapter_success(self, mock_logger):
        """Test successful chapter generation"""
        mock_self = MagicMock()
        mock_self.request.id = "chapter-gen-123"
        
        character_name = "Winston Churchill"
        chapter_number = 3
        chapter_title = "The War Years"
        
        result = generate_chapter(
            mock_self,
            character_name,
            chapter_number,
            chapter_title
        )
        
        assert result['success'] is True
        assert result['character_name'] == character_name
        assert result['chapter_number'] == chapter_number
        assert result['chapter_title'] == chapter_title
        assert 'content' in result
        assert 'word_count' in result
        assert 'task_id' in result
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_chapter_with_context(self, mock_logger):
        """Test chapter generation with additional context"""
        mock_self = MagicMock()
        mock_self.request.id = "chapter-gen-124"
        
        character_name = "Marie Curie"
        chapter_number = 1
        chapter_title = "Early Life"
        context = {
            "previous_chapters": [],
            "themes": ["science", "perseverance"],
            "target_length": 2550
        }
        
        result = generate_chapter(
            mock_self,
            character_name,
            chapter_number,
            chapter_title,
            context
        )
        
        assert result['success'] is True
        assert result['chapter_number'] == 1
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_chapter_target_length(self, mock_logger):
        """Test chapter generation with custom target length"""
        mock_self = MagicMock()
        mock_self.request.id = "chapter-gen-125"
        
        result = generate_chapter(
            mock_self,
            "Albert Einstein",
            2,
            "Academic Years",
            {"target_length": 3000}
        )
        
        assert result['success'] is True
        assert 'word_count' in result
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_chapter_multiple_calls(self, mock_logger):
        """Test generating multiple chapters"""
        mock_self = MagicMock()
        
        chapters = []
        for i in range(1, 4):
            mock_self.request.id = f"chapter-gen-{i}"
            result = generate_chapter(
                mock_self,
                "Leonardo da Vinci",
                i,
                f"Chapter {i}"
            )
            chapters.append(result)
        
        assert len(chapters) == 3
        for idx, chapter in enumerate(chapters, 1):
            assert chapter['chapter_number'] == idx
            assert chapter['success'] is True


class TestGenerateIntroduction:
    """Test generate_introduction task"""
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_introduction_success(self, mock_logger):
        """Test successful introduction generation"""
        mock_self = MagicMock()
        mock_self.request.id = "intro-gen-123"
        
        character_name = "Nikola Tesla"
        biography_context = {
            "themes": ["innovation", "electricity"],
            "key_achievements": ["AC electricity", "Tesla coil"]
        }
        
        result = generate_introduction(
            mock_self,
            character_name,
            biography_context
        )
        
        assert result['success'] is True
        assert result['character_name'] == character_name
        assert result['section'] == 'introduction'
        assert 'content' in result
        assert 'word_count' in result
        assert 'task_id' in result
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_introduction_minimal(self, mock_logger):
        """Test introduction generation with minimal context"""
        mock_self = MagicMock()
        mock_self.request.id = "intro-gen-124"
        
        result = generate_introduction(
            mock_self,
            "Ada Lovelace",
            {}
        )
        
        assert result['success'] is True
        assert result['section'] == 'introduction'
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_introduction_with_themes(self, mock_logger):
        """Test introduction generation with specific themes"""
        mock_self = MagicMock()
        mock_self.request.id = "intro-gen-125"
        
        context = {
            "themes": ["mathematics", "programming", "pioneering"],
            "time_period": "1815-1852"
        }
        
        result = generate_introduction(
            mock_self,
            "Ada Lovelace",
            context
        )
        
        assert result['success'] is True
        assert 'content' in result


class TestGenerateConclusion:
    """Test generate_conclusion task"""
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_conclusion_success(self, mock_logger):
        """Test successful conclusion generation"""
        mock_self = MagicMock()
        mock_self.request.id = "concl-gen-123"
        
        character_name = "Isaac Newton"
        biography_summary = {
            "key_points": ["gravity", "calculus", "optics"],
            "impact": "Revolutionary scientist"
        }
        
        result = generate_conclusion(
            mock_self,
            character_name,
            biography_summary
        )
        
        assert result['success'] is True
        assert result['character_name'] == character_name
        assert result['section'] == 'conclusion'
        assert 'content' in result
        assert 'word_count' in result
        assert 'task_id' in result
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_conclusion_with_legacy(self, mock_logger):
        """Test conclusion generation with legacy information"""
        mock_self = MagicMock()
        mock_self.request.id = "concl-gen-124"
        
        summary = {
            "key_points": ["leadership", "speeches", "strategy"],
            "legacy": "Wartime leader who saved democracy",
            "lasting_impact": "Political philosophy and literature"
        }
        
        result = generate_conclusion(
            mock_self,
            "Winston Churchill",
            summary
        )
        
        assert result['success'] is True
        assert result['section'] == 'conclusion'
    
    @patch('src.tasks.generation_tasks.logger')
    def test_generate_conclusion_minimal(self, mock_logger):
        """Test conclusion generation with minimal summary"""
        mock_self = MagicMock()
        mock_self.request.id = "concl-gen-125"
        
        result = generate_conclusion(
            mock_self,
            "Charles Darwin",
            {}
        )
        
        assert result['success'] is True
        assert 'content' in result


class TestGenerationTasksIntegration:
    """Integration tests for generation tasks"""
    
    @pytest.mark.integration
    @patch('src.tasks.generation_tasks.logger')
    def test_complete_generation_workflow(self, mock_logger):
        """Test complete biography generation workflow"""
        mock_self = MagicMock()
        character_name = "Galileo Galilei"
        
        # Generate introduction
        mock_self.request.id = "workflow-intro"
        intro_result = generate_introduction(
            mock_self,
            character_name,
            {"themes": ["astronomy", "physics"]}
        )
        assert intro_result['success'] is True
        
        # Generate chapters
        chapters = []
        for i in range(1, 4):
            mock_self.request.id = f"workflow-ch-{i}"
            chapter = generate_chapter(
                mock_self,
                character_name,
                i,
                f"Chapter {i}"
            )
            chapters.append(chapter)
            assert chapter['success'] is True
        
        # Generate conclusion
        mock_self.request.id = "workflow-concl"
        concl_result = generate_conclusion(
            mock_self,
            character_name,
            {"key_points": ["telescope", "heliocentrism"]}
        )
        assert concl_result['success'] is True
        
        # Verify all parts
        assert len(chapters) == 3
        assert intro_result['section'] == 'introduction'
        assert concl_result['section'] == 'conclusion'
    
    @pytest.mark.integration
    @patch('src.tasks.generation_tasks.logger')
    def test_chapter_sequence_consistency(self, mock_logger):
        """Test that chapters maintain sequence consistency"""
        mock_self = MagicMock()
        character_name = "Leonardo da Vinci"
        
        chapter_results = []
        for i in range(1, 6):
            mock_self.request.id = f"seq-ch-{i}"
            result = generate_chapter(
                mock_self,
                character_name,
                i,
                f"Chapter {i}: Part {i}"
            )
            chapter_results.append(result)
        
        # Verify sequence
        for idx, result in enumerate(chapter_results, 1):
            assert result['chapter_number'] == idx
            assert result['success'] is True
