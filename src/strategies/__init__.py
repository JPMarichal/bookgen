"""
Source search strategies package
"""
from .base_strategy import SourceStrategy, CharacterAnalysis
from .academic_database_strategy import AcademicDatabaseStrategy
from .government_archive_strategy import GovernmentArchiveStrategy
from .biography_website_strategy import BiographyWebsiteStrategy
from .news_archive_strategy import NewsArchiveStrategy

__all__ = [
    'SourceStrategy',
    'CharacterAnalysis',
    'AcademicDatabaseStrategy',
    'GovernmentArchiveStrategy',
    'BiographyWebsiteStrategy',
    'NewsArchiveStrategy',
]
