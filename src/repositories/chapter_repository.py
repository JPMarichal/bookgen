"""
Chapter repository
"""
from typing import List
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.chapter import Chapter
from .base import BaseRepository


class ChapterRepository(BaseRepository[Chapter]):
    """
    Repository for Chapter model with specific queries
    """
    
    def __init__(self, db: Session):
        super().__init__(Chapter, db)
    
    def get_by_biography(self, biography_id: int) -> List[Chapter]:
        """
        Get all chapters for a biography
        
        Args:
            biography_id: Biography ID
            
        Returns:
            List of chapters ordered by number
        """
        stmt = (
            select(Chapter)
            .where(Chapter.biography_id == biography_id)
            .order_by(Chapter.number)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_biography_and_number(self, biography_id: int, number: int) -> Chapter:
        """
        Get specific chapter by biography ID and chapter number
        
        Args:
            biography_id: Biography ID
            number: Chapter number
            
        Returns:
            Chapter or None if not found
        """
        stmt = (
            select(Chapter)
            .where(Chapter.biography_id == biography_id)
            .where(Chapter.number == number)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def count_by_biography(self, biography_id: int) -> int:
        """
        Count chapters for a biography
        
        Args:
            biography_id: Biography ID
            
        Returns:
            Total count of chapters
        """
        stmt = select(Chapter).where(Chapter.biography_id == biography_id)
        result = self.db.execute(stmt)
        return len(list(result.scalars().all()))
    
    def get_total_word_count(self, biography_id: int) -> int:
        """
        Get total word count for all chapters in a biography
        
        Args:
            biography_id: Biography ID
            
        Returns:
            Total word count
        """
        chapters = self.get_by_biography(biography_id)
        return sum(chapter.word_count for chapter in chapters)
