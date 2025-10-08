"""
Personalized Search Strategies - Dispatcher for character-specific search strategies
"""
from typing import Optional
from .base_strategy import CharacterAnalysis, SourceStrategy
from .scientific_figure_strategy import ScientificFigureStrategy
from .political_figure_strategy import PoliticalFigureStrategy
from .artistic_figure_strategy import ArtisticFigureStrategy
from .literary_figure_strategy import LiteraryFigureStrategy
from .military_figure_strategy import MilitaryFigureStrategy
from .academic_database_strategy import AcademicDatabaseStrategy


class PersonalizedSearchStrategies:
    """Estrategias de búsqueda especializadas por tipo de personaje"""
    
    def get_search_strategy(self, character_analysis: CharacterAnalysis) -> SourceStrategy:
        """
        Selecciona la estrategia óptima basada en el perfil del personaje
        
        Args:
            character_analysis: Analysis of the character including field information
            
        Returns:
            Appropriate specialized strategy for the character type
        """
        if not character_analysis or not character_analysis.field:
            # Default to general academic strategy if no field specified
            return AcademicDatabaseStrategy()
        
        field = character_analysis.field.lower()
        
        if field in ['science', 'physics', 'chemistry', 'biology', 'mathematics']:
            return ScientificFigureStrategy(character_analysis)
        elif field in ['politics', 'political', 'government', 'politician']:
            return PoliticalFigureStrategy(character_analysis)
        elif field in ['arts', 'art', 'painting', 'sculpture', 'music', 'composer']:
            return ArtisticFigureStrategy(character_analysis)
        elif field in ['literature', 'writing', 'poetry', 'author', 'writer', 'poet']:
            return LiteraryFigureStrategy(character_analysis)
        elif field in ['military', 'general', 'admiral', 'commander', 'war']:
            return MilitaryFigureStrategy(character_analysis)
        else:
            # Default to general academic strategy
            return AcademicDatabaseStrategy()


def get_personalized_strategy(character_name: str) -> SourceStrategy:
    """
    Convenience function to get strategy based on character name
    For now returns a simple implementation, can be enhanced with AI detection
    
    Args:
        character_name: Name of the historical figure
        
    Returns:
        Appropriate strategy instance
    """
    # Basic field detection based on known figures
    # In production, this would use AI analysis
    character_lower = character_name.lower()
    
    # Scientists
    if any(name in character_lower for name in ['einstein', 'curie', 'newton', 'darwin', 'tesla', 'galileo']):
        analysis = CharacterAnalysis(name=character_name, field='science')
        return ScientificFigureStrategy(analysis)
    
    # Politicians
    if any(name in character_lower for name in ['washington', 'lincoln', 'churchill', 'roosevelt', 'gandhi']):
        analysis = CharacterAnalysis(name=character_name, field='politics')
        return PoliticalFigureStrategy(analysis)
    
    # Artists
    if any(name in character_lower for name in ['picasso', 'vinci', 'monet', 'beethoven', 'mozart', 'bach']):
        analysis = CharacterAnalysis(name=character_name, field='arts')
        return ArtisticFigureStrategy(analysis)
    
    # Literary figures
    if any(name in character_lower for name in ['shakespeare', 'dickens', 'twain', 'hemingway', 'austen']):
        analysis = CharacterAnalysis(name=character_name, field='literature')
        return LiteraryFigureStrategy(analysis)
    
    # Military figures
    if any(name in character_lower for name in ['napoleon', 'alexander', 'caesar', 'patton', 'macarthur']):
        analysis = CharacterAnalysis(name=character_name, field='military')
        return MilitaryFigureStrategy(analysis)
    
    # Default to academic strategy
    analysis = CharacterAnalysis(name=character_name)
    return AcademicDatabaseStrategy()
