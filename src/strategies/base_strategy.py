"""
Base strategy class for source searching
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field as dataclass_field
from typing import List, Optional, Dict, Any
from ..api.models.sources import SourceItem


@dataclass
class CharacterAnalysis:
    """Character analysis data for informed source searching"""
    name: str
    field: Optional[str] = None  # e.g., "science", "politics", "arts"
    era: Optional[str] = None  # e.g., "20th century", "Renaissance"
    nationality: Optional[str] = None
    institutions: List[str] = dataclass_field(default_factory=list)
    keywords: List[str] = dataclass_field(default_factory=list)
    specialty: Optional[str] = None


@dataclass
class SourceCandidate:
    """Source candidate with quality metadata"""
    source_item: SourceItem
    quality_score: float = 0.0
    relevance_score: float = 0.0
    credibility_score: float = 0.0
    metadata: Dict[str, Any] = dataclass_field(default_factory=dict)


class SourceStrategy(ABC):
    """Abstract base class for source search strategies"""
    
    @abstractmethod
    def search(
        self,
        character: str,
        context: Optional[CharacterAnalysis] = None
    ) -> List[SourceCandidate]:
        """
        Search for sources using this strategy
        
        Args:
            character: Character name to search for
            context: Optional character analysis for informed searching
            
        Returns:
            List of source candidates with quality scores
        """
        pass
    
    def _calculate_quality_score(
        self,
        relevance: float,
        credibility: float,
        completeness: float = 0.8,
        uniqueness: float = 0.5
    ) -> float:
        """
        Calculate overall quality score using weighted formula
        
        Args:
            relevance: Relevance score (0-1)
            credibility: Credibility score (0-100)
            completeness: Content completeness (0-1)
            uniqueness: Information uniqueness (0-1)
            
        Returns:
            Quality score (0-100)
        """
        # Normalize credibility to 0-1
        norm_credibility = credibility / 100.0
        
        # Weighted calculation matching system requirements
        weights = {
            'credibility': 0.30,
            'relevance': 0.35,
            'technical': 0.25,
            'uniqueness': 0.10
        }
        
        score = (
            norm_credibility * weights['credibility'] +
            relevance * weights['relevance'] +
            completeness * weights['technical'] +
            uniqueness * weights['uniqueness']
        ) * 100
        
        return round(score, 2)
