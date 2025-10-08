"""
Strategies package for source generation
"""
from .source_strategy import SourceStrategy
from .base_strategy import CharacterAnalysis, SourceCandidate
from .academic_database_strategy import AcademicDatabaseStrategy
from .government_archive_strategy import GovernmentArchiveStrategy
from .biography_website_strategy import BiographyWebsiteStrategy
from .news_archive_strategy import NewsArchiveStrategy
from .wikipedia_strategy import WikipediaStrategy
from .personalized_strategies import PersonalizedSearchStrategies, get_personalized_strategy
from .scientific_figure_strategy import ScientificFigureStrategy
from .political_figure_strategy import PoliticalFigureStrategy
from .artistic_figure_strategy import ArtisticFigureStrategy
from .literary_figure_strategy import LiteraryFigureStrategy
from .military_figure_strategy import MilitaryFigureStrategy

__all__ = [
    'SourceStrategy',
    'CharacterAnalysis',
    'SourceCandidate',
    'AcademicDatabaseStrategy',
    'GovernmentArchiveStrategy',
    'BiographyWebsiteStrategy',
    'NewsArchiveStrategy',
    'WikipediaStrategy',
    'PersonalizedSearchStrategies',
    'get_personalized_strategy',
    'ScientificFigureStrategy',
    'PoliticalFigureStrategy',
    'ArtisticFigureStrategy',
    'LiteraryFigureStrategy',
    'MilitaryFigureStrategy',
]
