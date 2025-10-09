"""
Intelligent content concatenation service
Migrates and enhances functionality from concat.py with smart features
"""
import os
import re
import unicodedata
from pathlib import Path
from typing import List, Optional, Dict
import logging

from src.api.models.concatenation import (
    ConcatenationResult,
    ConcatenationMetrics,
    ConcatenationConfig,
    ChapterContent,
    TransitionError,
    CoherenceIssue
)
from src.utils.narrative_analyzer import NarrativeAnalyzer
from src.utils.transition_generator import TransitionGenerator
from src.utils.text_analyzer import TextAnalyzer

logger = logging.getLogger(__name__)


class ConcatenationService:
    """Service for intelligent biography concatenation"""
    
    def __init__(self, config: Optional[ConcatenationConfig] = None):
        """
        Initialize concatenation service
        
        Args:
            config: Concatenation configuration (uses defaults if not provided)
        """
        self.config = config or ConcatenationConfig()
        self.narrative_analyzer = NarrativeAnalyzer()
        self.transition_generator = TransitionGenerator(
            enable_smart_transitions=self.config.enable_transition_generation
        )
        self.text_analyzer = TextAnalyzer()
    
    def concatenate_biography(
        self,
        character: str,
        validate_quality: bool = True
    ) -> ConcatenationResult:
        """
        Concatenate all files for a biography with intelligent analysis
        
        Args:
            character: Character/person name (normalized)
            validate_quality: Whether to perform quality validation
            
        Returns:
            ConcatenationResult with comprehensive metrics
        """
        logger.info(f"Starting concatenation for: {character}")
        
        # Get ordered files
        base_dir = os.path.join(self.config.base_path, character)
        files_to_concat = self._get_ordered_files(base_dir)
        
        # Check for missing files
        missing_files = self._check_missing_files(files_to_concat)
        
        # Load chapter contents
        chapters = self._load_chapters(files_to_concat)
        
        # Perform quality analysis if enabled
        coherence_score = 0.0
        transition_errors = []
        coherence_issues = []
        chronology_valid = True
        redundancies_removed = 0
        
        if validate_quality and chapters:
            # Analyze narrative coherence
            coherence_analysis = self.narrative_analyzer.analyze_coherence(
                [ch.content for ch in chapters],
                character
            )
            coherence_score = coherence_analysis['score']
            
            # Convert issues to CoherenceIssue objects
            for issue in coherence_analysis.get('issues', []):
                coherence_issues.append(CoherenceIssue(
                    location=issue.get('location', 'Unknown'),
                    issue_type=issue.get('type', 'unknown'),
                    severity=issue.get('severity', 'info'),
                    description=issue.get('message', ''),
                    context=issue.get('context')
                ))
            
            # Check chronology
            chronology_valid = coherence_analysis['metrics'].get(
                'temporal_consistency', 1.0
            ) >= 0.7
            
            # Analyze transitions
            if self.config.enable_transition_generation:
                transition_results = self.transition_generator.analyze_all_transitions(
                    [ch.content for ch in chapters]
                )
                
                for trans in transition_results:
                    if trans.get('has_errors'):
                        for issue in trans.get('issues', []):
                            transition_errors.append(TransitionError(
                                chapter_from=trans['from_section'],
                                chapter_to=trans['to_section'],
                                severity=issue.get('severity', 'info'),
                                message=issue.get('message', ''),
                                suggestion=issue.get('suggestion')
                            ))
            
            # Detect redundancies
            if self.config.enable_redundancy_detection:
                redundancies = self.narrative_analyzer.detect_redundancies(
                    [ch.content for ch in chapters]
                )
                redundancies_removed = len(redundancies)
        
        # Concatenate content
        final_content = self._concatenate_content(chapters)
        
        # Normalize headers for table of contents
        final_content = self.transition_generator.normalize_section_headers(
            final_content
        )
        
        # Generate output path
        output_file = self._generate_output_path(character, base_dir)
        
        # Write final file
        success = self._write_final_file(output_file, final_content)
        
        # Calculate metrics
        total_words = self.text_analyzer.count_words(final_content)
        
        # Calculate vocabulary richness
        words = re.findall(r'\b\w+\b', final_content.lower())
        unique_words = len(set(words))
        vocabulary_richness = unique_words / len(words) if words else 0.0
        
        metrics = ConcatenationMetrics(
            total_words=total_words,
            total_chapters=len([ch for ch in chapters if ch.section_type == 'chapter']),
            files_processed=len(chapters),
            missing_files=missing_files,
            coherence_score=coherence_score,
            transition_quality=self._calculate_transition_quality(transition_errors),
            redundancy_ratio=redundancies_removed / len(chapters) if chapters else 0.0,
            vocabulary_richness=vocabulary_richness
        )
        
        # Generate index (table of contents)
        index_generated = self._generate_index(final_content, output_file)
        
        result = ConcatenationResult(
            character=character,
            output_file=output_file,
            success=success,
            metrics=metrics,
            coherence_score=coherence_score,
            chronology_valid=chronology_valid,
            transition_errors=transition_errors,
            coherence_issues=coherence_issues,
            redundancies_removed=redundancies_removed,
            index_generated=index_generated
        )
        
        logger.info(
            f"Concatenation complete. Quality: {coherence_score:.2f}, "
            f"Words: {total_words}, Success: {success}"
        )
        
        return result
    
    def concatenate_chapters(
        self,
        chapters_list: List[Dict[str, str]]
    ) -> ConcatenationResult:
        """
        Concatenate a list of chapter dictionaries
        
        Args:
            chapters_list: List of dicts with 'title' and 'content' keys
            
        Returns:
            ConcatenationResult
        """
        # Convert to ChapterContent objects
        chapters = []
        for idx, chapter_dict in enumerate(chapters_list):
            chapters.append(ChapterContent(
                number=idx + 1,
                title=chapter_dict.get('title', f'Chapter {idx + 1}'),
                content=chapter_dict.get('content', ''),
                file_path='',
                word_count=self.text_analyzer.count_words(
                    chapter_dict.get('content', '')
                ),
                section_type='chapter'
            ))
        
        # Analyze coherence
        coherence_analysis = self.narrative_analyzer.analyze_coherence(
            [ch.content for ch in chapters],
            'Subject'  # Generic name when not specified
        )
        
        # Analyze transitions
        transition_results = self.transition_generator.analyze_all_transitions(
            [ch.content for ch in chapters]
        )
        
        transition_errors = []
        for trans in transition_results:
            if trans.get('has_errors'):
                for issue in trans.get('issues', []):
                    transition_errors.append(TransitionError(
                        chapter_from=trans['from_section'],
                        chapter_to=trans['to_section'],
                        severity=issue.get('severity', 'info'),
                        message=issue.get('message', '')
                    ))
        
        # Concatenate
        final_content = self._concatenate_content(chapters)
        total_words = self.text_analyzer.count_words(final_content)
        
        # Build result
        coherence_score = coherence_analysis['score']
        chronology_valid = coherence_analysis['metrics'].get(
            'temporal_consistency', 1.0
        ) >= 0.7
        
        metrics = ConcatenationMetrics(
            total_words=total_words,
            total_chapters=len(chapters),
            files_processed=len(chapters),
            coherence_score=coherence_score,
            transition_quality=self._calculate_transition_quality(transition_errors)
        )
        
        return ConcatenationResult(
            character='',
            output_file='',
            success=True,
            metrics=metrics,
            coherence_score=coherence_score,
            chronology_valid=chronology_valid,
            transition_errors=transition_errors
        )
    
    def _get_ordered_files(self, base_dir: str) -> List[str]:
        """
        Get list of files in correct order from new directory structure
        
        Args:
            base_dir: Base directory path
            
        Returns:
            List of file paths
        """
        file_paths = []
        
        for filename in self.config.file_order:
            # Determine subdirectory based on file type
            if filename.startswith('capitulo-') or filename.startswith('chapter-'):
                # Chapters go in chapters/
                file_path = os.path.join(base_dir, 'chapters', filename)
            else:
                # All other files (sections) go in sections/
                file_path = os.path.join(base_dir, 'sections', filename)
            
            file_paths.append(file_path)
        
        return file_paths
    
    def _check_missing_files(self, file_paths: List[str]) -> List[str]:
        """
        Check which files are missing
        
        Args:
            file_paths: List of file paths to check
            
        Returns:
            List of missing file names
        """
        missing = []
        for file_path in file_paths:
            if not os.path.exists(file_path):
                missing.append(os.path.basename(file_path))
        return missing
    
    def _load_chapters(self, file_paths: List[str]) -> List[ChapterContent]:
        """
        Load chapter contents from files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of ChapterContent objects
        """
        chapters = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                filename = os.path.basename(file_path)
                
                # Determine section type and number
                section_type = self._get_section_type(filename)
                chapter_number = self._extract_chapter_number(filename)
                
                # Extract title from content or filename
                title = self._extract_title(content, filename)
                
                word_count = self.text_analyzer.count_words(content)
                
                chapters.append(ChapterContent(
                    number=chapter_number,
                    title=title,
                    content=content,
                    file_path=file_path,
                    word_count=word_count,
                    section_type=section_type
                ))
                
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
        
        return chapters
    
    def _get_section_type(self, filename: str) -> str:
        """Determine section type from filename"""
        filename_lower = filename.lower()
        
        if 'prologo' in filename_lower or 'prologue' in filename_lower:
            return 'prologue'
        elif 'introduccion' in filename_lower or 'introduction' in filename_lower:
            return 'introduction'
        elif 'cronologia' in filename_lower or 'timeline' in filename_lower:
            return 'timeline'
        elif 'capitulo' in filename_lower or 'chapter' in filename_lower:
            return 'chapter'
        elif 'epilogo' in filename_lower or 'epilogue' in filename_lower:
            return 'epilogue'
        elif 'glosario' in filename_lower or 'glossary' in filename_lower:
            return 'glossary'
        elif 'dramatis' in filename_lower:
            return 'dramatis_personae'
        elif 'fuentes' in filename_lower or 'sources' in filename_lower:
            return 'sources'
        else:
            return 'other'
    
    def _extract_chapter_number(self, filename: str) -> Optional[int]:
        """Extract chapter number from filename"""
        match = re.search(r'capitulo-?(\d+)|chapter-?(\d+)', filename, re.IGNORECASE)
        if match:
            return int(match.group(1) or match.group(2))
        return None
    
    def _extract_title(self, content: str, filename: str) -> str:
        """Extract title from content or generate from filename"""
        # Try to find first header
        for line in content.split('\n')[:10]:
            if line.strip().startswith('#'):
                title = re.sub(r'^#+\s*', '', line).strip()
                if title:
                    return title
        
        # Fallback to filename
        return os.path.splitext(filename)[0].replace('-', ' ').title()
    
    def _concatenate_content(self, chapters: List[ChapterContent]) -> str:
        """
        Concatenate chapter contents with transitions
        
        Args:
            chapters: List of chapter contents
            
        Returns:
            Concatenated content string
        """
        if not chapters:
            return ""
        
        parts = []
        
        for i, chapter in enumerate(chapters):
            # Add chapter content
            parts.append(chapter.content)
            
            # Add transition (except after last chapter)
            if i < len(chapters) - 1:
                transition = self.transition_generator.generate_transition(
                    chapter.content,
                    chapters[i + 1].content
                )
                parts.append(transition)
        
        return ''.join(parts)
    
    def _generate_output_path(self, character: str, base_dir: str) -> str:
        """
        Generate output file path in output/markdown/ subdirectory
        
        Args:
            character: Character name
            base_dir: Base directory
            
        Returns:
            Output file path
        """
        # Use template from config
        filename = self.config.output_filename_template.format(character=character)
        
        # Remove diacritics for file safety
        filename = self._remove_diacritics(filename)
        
        # Place in output/markdown/ subdirectory
        return os.path.join(base_dir, 'output', 'markdown', filename)
    
    def _remove_diacritics(self, text: str) -> str:
        """Remove diacritics from text for safe filenames"""
        normalized = unicodedata.normalize('NFD', text)
        without_diacritics = ''.join(
            char for char in normalized
            if unicodedata.category(char) != 'Mn'
        )
        return unicodedata.normalize('NFC', without_diacritics)
    
    def _write_final_file(self, output_path: str, content: str) -> bool:
        """
        Write final concatenated file
        
        Args:
            output_path: Output file path
            content: Content to write
            
        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            
            logger.info(f"Successfully wrote: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing file {output_path}: {e}")
            return False
    
    def _calculate_transition_quality(
        self,
        transition_errors: List[TransitionError]
    ) -> float:
        """
        Calculate overall transition quality score
        
        Args:
            transition_errors: List of transition errors
            
        Returns:
            Quality score (0-1)
        """
        if not transition_errors:
            return 1.0
        
        # Penalize based on number and severity of errors
        critical_errors = sum(1 for e in transition_errors if e.severity == 'critical')
        warning_errors = sum(1 for e in transition_errors if e.severity == 'warning')
        
        penalty = (critical_errors * 0.3) + (warning_errors * 0.1)
        
        return max(0.0, 1.0 - penalty)
    
    def _generate_index(self, content: str, output_file: str) -> bool:
        """
        Generate table of contents index
        
        Args:
            content: Full content
            output_file: Output file path
            
        Returns:
            True if index was generated
        """
        # Extract all headers
        headers = []
        for line in content.split('\n'):
            match = re.match(r'^(#+)\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headers.append((level, title))
        
        # Index is considered generated if we found headers
        return len(headers) > 0
