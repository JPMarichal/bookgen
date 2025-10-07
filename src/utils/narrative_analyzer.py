"""
Narrative coherence analyzer for biography content
Analyzes text for narrative flow, consistency, and quality
"""
import re
from typing import List, Dict, Tuple, Optional
from collections import Counter
import logging

from src.utils.text_analyzer import TextAnalyzer

logger = logging.getLogger(__name__)


class NarrativeAnalyzer:
    """Analyzes narrative coherence and quality"""
    
    def __init__(self):
        """Initialize narrative analyzer"""
        self.text_analyzer = TextAnalyzer()
    
    def analyze_coherence(
        self, 
        chapters: List[str],
        character_name: str
    ) -> Dict[str, any]:
        """
        Analyze narrative coherence across multiple chapters
        
        Args:
            chapters: List of chapter contents
            character_name: Biography subject name
            
        Returns:
            Dictionary with coherence metrics
        """
        if not chapters:
            return {
                'score': 0.0,
                'issues': [],
                'metrics': {}
            }
        
        # Analyze various coherence aspects
        character_consistency = self._check_character_consistency(chapters, character_name)
        temporal_consistency = self._check_temporal_consistency(chapters)
        vocabulary_coherence = self._check_vocabulary_coherence(chapters)
        narrative_flow = self._analyze_narrative_flow(chapters)
        
        # Calculate overall coherence score (weighted average)
        overall_score = (
            character_consistency['score'] * 0.3 +
            temporal_consistency['score'] * 0.2 +
            vocabulary_coherence['score'] * 0.25 +
            narrative_flow['score'] * 0.25
        )
        
        # Collect all issues
        all_issues = []
        all_issues.extend(character_consistency.get('issues', []))
        all_issues.extend(temporal_consistency.get('issues', []))
        all_issues.extend(vocabulary_coherence.get('issues', []))
        all_issues.extend(narrative_flow.get('issues', []))
        
        return {
            'score': overall_score,
            'issues': all_issues,
            'metrics': {
                'character_consistency': character_consistency['score'],
                'temporal_consistency': temporal_consistency['score'],
                'vocabulary_coherence': vocabulary_coherence['score'],
                'narrative_flow': narrative_flow['score']
            }
        }
    
    def _check_character_consistency(
        self, 
        chapters: List[str],
        character_name: str
    ) -> Dict[str, any]:
        """
        Check for consistent character representation
        
        Args:
            chapters: List of chapter contents
            character_name: Biography subject name
            
        Returns:
            Consistency analysis
        """
        issues = []
        
        # Extract first and last name variations
        name_parts = character_name.split()
        name_patterns = []
        
        if len(name_parts) >= 2:
            # Full name
            name_patterns.append(character_name)
            # Last name
            name_patterns.append(name_parts[-1])
            # First name
            name_patterns.append(name_parts[0])
        else:
            name_patterns.append(character_name)
        
        # Count mentions across chapters
        total_mentions = 0
        chapters_with_mentions = 0
        
        for idx, chapter in enumerate(chapters):
            chapter_mentions = 0
            for pattern in name_patterns:
                # Case-insensitive search
                chapter_mentions += len(re.findall(
                    r'\b' + re.escape(pattern) + r'\b',
                    chapter,
                    re.IGNORECASE
                ))
            
            if chapter_mentions > 0:
                chapters_with_mentions += 1
            total_mentions += chapter_mentions
        
        # Calculate consistency score
        if len(chapters) == 0:
            score = 0.0
        else:
            # Score based on percentage of chapters mentioning the subject
            mention_ratio = chapters_with_mentions / len(chapters)
            
            # Also consider average mentions per chapter
            avg_mentions = total_mentions / len(chapters)
            
            # Combine metrics (good if most chapters mention the subject)
            score = min(1.0, (mention_ratio * 0.7 + min(avg_mentions / 10, 1.0) * 0.3))
        
        # Flag issues
        if score < 0.5:
            issues.append({
                'type': 'character_consistency',
                'severity': 'warning',
                'message': f'Subject "{character_name}" mentioned in only {chapters_with_mentions}/{len(chapters)} sections'
            })
        
        return {
            'score': score,
            'issues': issues,
            'total_mentions': total_mentions
        }
    
    def _check_temporal_consistency(self, chapters: List[str]) -> Dict[str, any]:
        """
        Check temporal/chronological consistency
        
        Args:
            chapters: List of chapter contents
            
        Returns:
            Temporal consistency analysis
        """
        issues = []
        
        # Extract year mentions
        year_pattern = r'\b(1[0-9]{3}|20[0-2][0-9])\b'
        
        chapter_years = []
        for chapter in chapters:
            years = re.findall(year_pattern, chapter)
            if years:
                # Get unique years and convert to int
                unique_years = sorted(set(int(y) for y in years))
                chapter_years.append(unique_years)
            else:
                chapter_years.append([])
        
        # Check for chronological progression
        score = 1.0
        
        for i in range(len(chapter_years) - 1):
            if chapter_years[i] and chapter_years[i + 1]:
                # Get the latest year from current chapter
                current_max = max(chapter_years[i])
                # Get the earliest year from next chapter
                next_min = min(chapter_years[i + 1])
                
                # Flag if there's a significant backward jump
                if next_min < current_max - 5:  # Allow some overlap
                    issues.append({
                        'type': 'timeline_conflict',
                        'severity': 'warning',
                        'message': f'Potential chronology issue between chapters {i+1} and {i+2}: years jump from {current_max} back to {next_min}'
                    })
                    score -= 0.1
        
        score = max(0.0, score)
        
        return {
            'score': score,
            'issues': issues
        }
    
    def _check_vocabulary_coherence(self, chapters: List[str]) -> Dict[str, any]:
        """
        Analyze vocabulary consistency across chapters
        
        Args:
            chapters: List of chapter contents
            
        Returns:
            Vocabulary coherence metrics
        """
        if len(chapters) < 2:
            return {'score': 1.0, 'issues': []}
        
        # Combine all chapters
        combined_text = ' '.join(chapters)
        
        # Calculate vocabulary richness
        words = re.findall(r'\b\w+\b', combined_text.lower())
        if not words:
            return {'score': 0.0, 'issues': []}
        
        unique_words = set(words)
        vocabulary_richness = len(unique_words) / len(words)
        
        # Analyze vocabulary distribution across chapters
        chapter_vocabularies = []
        for chapter in chapters:
            chapter_words = set(re.findall(r'\b\w+\b', chapter.lower()))
            chapter_vocabularies.append(chapter_words)
        
        # Calculate overlap between consecutive chapters
        overlaps = []
        for i in range(len(chapter_vocabularies) - 1):
            vocab1 = chapter_vocabularies[i]
            vocab2 = chapter_vocabularies[i + 1]
            
            if vocab1 and vocab2:
                intersection = len(vocab1 & vocab2)
                union = len(vocab1 | vocab2)
                overlap = intersection / union if union > 0 else 0
                overlaps.append(overlap)
        
        # Good coherence has moderate overlap (not too much, not too little)
        avg_overlap = sum(overlaps) / len(overlaps) if overlaps else 0
        
        # Score based on overlap (ideal is 0.3-0.6)
        if 0.3 <= avg_overlap <= 0.6:
            score = 1.0
        elif avg_overlap < 0.3:
            # Too little overlap might indicate inconsistency
            score = max(0.5, avg_overlap / 0.3)
        else:
            # Too much overlap might indicate redundancy
            score = max(0.5, 1.0 - (avg_overlap - 0.6) / 0.4)
        
        issues = []
        if score < 0.7:
            issues.append({
                'type': 'vocabulary_coherence',
                'severity': 'info',
                'message': f'Vocabulary consistency score is {score:.2f}. Average overlap: {avg_overlap:.2f}'
            })
        
        return {
            'score': score,
            'issues': issues,
            'vocabulary_richness': vocabulary_richness
        }
    
    def _analyze_narrative_flow(self, chapters: List[str]) -> Dict[str, any]:
        """
        Analyze narrative flow and transitions
        
        Args:
            chapters: List of chapter contents
            
        Returns:
            Narrative flow metrics
        """
        issues = []
        score = 1.0
        
        # Check for abrupt starts/ends
        for idx, chapter in enumerate(chapters):
            if not chapter.strip():
                continue
            
            lines = chapter.strip().split('\n')
            
            # Check for proper chapter structure
            has_header = False
            for line in lines[:5]:  # Check first 5 lines
                if re.match(r'^#+\s+', line):
                    has_header = True
                    break
            
            if not has_header and idx > 0:  # Allow first chapter to be different
                issues.append({
                    'type': 'structure',
                    'severity': 'info',
                    'message': f'Section {idx+1} may lack proper header structure'
                })
                score -= 0.05
        
        score = max(0.0, score)
        
        return {
            'score': score,
            'issues': issues
        }
    
    def detect_redundancies(
        self,
        chapters: List[str],
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, any]]:
        """
        Detect redundant content across chapters
        
        Args:
            chapters: List of chapter contents
            similarity_threshold: Threshold for considering content redundant
            
        Returns:
            List of detected redundancies
        """
        redundancies = []
        
        # Split chapters into paragraphs
        chapter_paragraphs = []
        for idx, chapter in enumerate(chapters):
            paragraphs = [p.strip() for p in chapter.split('\n\n') if p.strip()]
            chapter_paragraphs.append((idx, paragraphs))
        
        # Simple redundancy detection based on exact or near-exact matches
        seen_content = {}
        
        for chapter_idx, paragraphs in chapter_paragraphs:
            for para_idx, paragraph in enumerate(paragraphs):
                # Skip very short paragraphs
                if len(paragraph.split()) < 10:
                    continue
                
                # Normalize paragraph for comparison
                normalized = ' '.join(paragraph.lower().split())
                
                # Check for duplicates
                if normalized in seen_content:
                    original_chapter, original_para = seen_content[normalized]
                    redundancies.append({
                        'type': 'exact_duplicate',
                        'original_chapter': original_chapter,
                        'duplicate_chapter': chapter_idx,
                        'severity': 'warning',
                        'message': f'Duplicate content found between chapters {original_chapter+1} and {chapter_idx+1}'
                    })
                else:
                    seen_content[normalized] = (chapter_idx, para_idx)
        
        return redundancies
