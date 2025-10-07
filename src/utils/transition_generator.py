"""
Intelligent transition generator for chapter concatenation
Generates natural transitions between biography sections
"""
import re
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)


class TransitionGenerator:
    """Generates smooth transitions between chapters"""
    
    # Transition templates for different contexts
    TRANSITION_TEMPLATES = {
        'chronological': [
            "\n\n---\n\n",  # Simple section break
        ],
        'thematic': [
            "\n\n---\n\n",
        ],
        'default': [
            "\n\n---\n\n",
        ]
    }
    
    def __init__(self, enable_smart_transitions: bool = True):
        """
        Initialize transition generator
        
        Args:
            enable_smart_transitions: Whether to generate contextual transitions
        """
        self.enable_smart_transitions = enable_smart_transitions
    
    def generate_transition(
        self,
        previous_section: str,
        next_section: str,
        transition_type: str = 'default'
    ) -> str:
        """
        Generate a transition between two sections
        
        Args:
            previous_section: Content of previous section
            next_section: Content of next section
            transition_type: Type of transition to generate
            
        Returns:
            Transition text
        """
        if not self.enable_smart_transitions:
            return "\n\n"
        
        # For now, use simple section breaks
        # Future enhancement: could analyze content and generate contextual transitions
        templates = self.TRANSITION_TEMPLATES.get(
            transition_type,
            self.TRANSITION_TEMPLATES['default']
        )
        
        return templates[0]
    
    def validate_transition(
        self,
        previous_section: str,
        next_section: str
    ) -> Dict[str, any]:
        """
        Validate transition quality between sections
        
        Args:
            previous_section: Content of previous section
            next_section: Content of next section
            
        Returns:
            Validation result with score and issues
        """
        issues = []
        score = 1.0
        
        # Check for abrupt topic changes
        prev_last_para = self._get_last_paragraph(previous_section)
        next_first_para = self._get_first_paragraph(next_section)
        
        # Check if next section starts properly
        if next_first_para and not self._has_proper_header(next_first_para):
            issues.append({
                'type': 'missing_header',
                'severity': 'info',
                'message': 'Next section may lack proper header'
            })
            score -= 0.1
        
        # Check for repetitive openings
        if prev_last_para and next_first_para:
            if self._are_similar(prev_last_para, next_first_para):
                issues.append({
                    'type': 'repetitive_content',
                    'severity': 'warning',
                    'message': 'Potential repetitive content at section boundary'
                })
                score -= 0.2
        
        return {
            'score': max(0.0, score),
            'issues': issues,
            'has_errors': len(issues) > 0
        }
    
    def _get_last_paragraph(self, text: str) -> Optional[str]:
        """Extract last paragraph from text"""
        if not text:
            return None
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs[-1] if paragraphs else None
    
    def _get_first_paragraph(self, text: str) -> Optional[str]:
        """Extract first paragraph from text"""
        if not text:
            return None
        
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return paragraphs[0] if paragraphs else None
    
    def _has_proper_header(self, text: str) -> bool:
        """Check if text starts with a proper markdown header"""
        if not text:
            return False
        
        first_line = text.split('\n')[0].strip()
        return bool(re.match(r'^#+\s+', first_line))
    
    def _are_similar(self, text1: str, text2: str, threshold: float = 0.6) -> bool:
        """
        Check if two texts are similar
        
        Args:
            text1: First text
            text2: Second text
            threshold: Similarity threshold (0-1)
            
        Returns:
            True if texts are similar
        """
        if not text1 or not text2:
            return False
        
        # Simple word-based similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return False
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= threshold
    
    def analyze_all_transitions(
        self,
        sections: List[str]
    ) -> List[Dict[str, any]]:
        """
        Analyze all transitions in a sequence of sections
        
        Args:
            sections: List of section contents
            
        Returns:
            List of transition analyses
        """
        results = []
        
        for i in range(len(sections) - 1):
            result = self.validate_transition(sections[i], sections[i + 1])
            result['from_section'] = i
            result['to_section'] = i + 1
            results.append(result)
        
        return results
    
    def normalize_section_headers(self, content: str) -> str:
        """
        Normalize section headers for proper structure
        
        Args:
            content: Section content
            
        Returns:
            Content with normalized headers
        """
        # Ensure main sections use # (level 1) headers
        main_section_patterns = [
            (r'^##+ (Prólogo)', r'# \1'),
            (r'^##+ (Introducción|Introduccion)', r'# \1'),
            (r'^##+ (Cronología|Cronologia)', r'# \1'),
            (r'^##+ (Capítulo \d+|Capitulo \d+)', r'# \1'),
            (r'^##+ (Epílogo|Epilogo)', r'# \1'),
            (r'^##+ (Glosario)', r'# \1'),
            (r'^##+ (Dramatis Personae)', r'# \1'),
            (r'^##+ (Fuentes)', r'# \1'),
            # English versions
            (r'^##+ (Prologue)', r'# \1'),
            (r'^##+ (Introduction)', r'# \1'),
            (r'^##+ (Timeline|Chronology)', r'# \1'),
            (r'^##+ (Chapter \d+)', r'# \1'),
            (r'^##+ (Epilogue)', r'# \1'),
            (r'^##+ (Glossary)', r'# \1'),
            (r'^##+ (Cast of Characters)', r'# \1'),
            (r'^##+ (Sources)', r'# \1'),
        ]
        
        result = content
        for pattern, replacement in main_section_patterns:
            result = re.sub(pattern, replacement, result, flags=re.MULTILINE)
        
        return result
