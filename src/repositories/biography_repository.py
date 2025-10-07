"""
Biography repository
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.biography import Biography
from .base import BaseRepository


class BiographyRepository(BaseRepository[Biography]):
    """
    Repository for Biography model with specific queries
    """
    
    def __init__(self, db: Session):
        super().__init__(Biography, db)
    
    def get_by_character_name(self, character_name: str) -> Optional[Biography]:
        """
        Get biography by character name
        
        Args:
            character_name: Character name to search for
            
        Returns:
            Biography or None if not found
        """
        stmt = select(Biography).where(Biography.character_name == character_name)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Biography]:
        """
        Get biographies by status
        
        Args:
            status: Status to filter by (pending, in_progress, completed, failed)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of biographies
        """
        stmt = (
            select(Biography)
            .where(Biography.status == status)
            .order_by(Biography.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_with_chapters(self, id: int) -> Optional[Biography]:
        """
        Get biography by ID with chapters eagerly loaded
        
        Args:
            id: Biography ID
            
        Returns:
            Biography with chapters or None if not found
        """
        stmt = (
            select(Biography)
            .where(Biography.id == id)
            .options(joinedload(Biography.chapters))
        )
        result = self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    def get_recent(self, limit: int = 10) -> List[Biography]:
        """
        Get most recent biographies
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent biographies
        """
        stmt = (
            select(Biography)
            .order_by(Biography.created_at.desc())
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
