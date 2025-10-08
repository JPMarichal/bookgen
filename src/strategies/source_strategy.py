"""
Base interface for source generation strategies
"""
from abc import ABC, abstractmethod
from typing import List
import logging

from ..api.models.sources import SourceItem
from ..api.models.source_generation import CharacterAnalysis

logger = logging.getLogger(__name__)


class SourceStrategy(ABC):
    """
    Abstract base class for source generation strategies
    
    Each strategy implements a specific method for finding sources
    (e.g., Wikipedia, academic databases, government archives)
    """
    
    def __init__(self):
        """Initialize the strategy"""
        self.name = self.__class__.__name__
        logger.info(f"Initialized {self.name}")
    
    @abstractmethod
    def search(
        self,
        character_name: str,
        character_analysis: CharacterAnalysis
    ) -> List[SourceItem]:
        """
        Search for sources using this strategy
        
        Args:
            character_name: Name of the character to search for
            character_analysis: AI analysis of the character with context
            
        Returns:
            List of SourceItem objects found by this strategy
        """
        pass
    
    def get_strategy_name(self) -> str:
        """
        Get the name of this strategy
        
        Returns:
            Strategy name
        """
        return self.name
