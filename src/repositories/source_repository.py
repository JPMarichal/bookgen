"""
Source repository
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.source import Source
from .base import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """
    Repository for Source model with specific queries
    """
    
    def __init__(self, db: Session):
        super().__init__(Source, db)
    
    def get_by_url(self, url: str) -> Optional[Source]:
        """
        Get source by URL
        
        Args:
            url: Source URL
            
        Returns:
            Source or None if not found
        """
        stmt = select(Source).where(Source.url == url)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_by_validation_status(
        self, 
        validation_status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Source]:
        """
        Get sources by validation status
        
        Args:
            validation_status: Validation status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of sources
        """
        stmt = (
            select(Source)
            .where(Source.validation_status == validation_status)
            .order_by(Source.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_relevance_threshold(
        self, 
        min_relevance: float, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Source]:
        """
        Get sources above a relevance threshold
        
        Args:
            min_relevance: Minimum relevance score
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of sources ordered by relevance score descending
        """
        stmt = (
            select(Source)
            .where(Source.relevance_score >= min_relevance)
            .order_by(Source.relevance_score.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_valid_sources(self, skip: int = 0, limit: int = 100) -> List[Source]:
        """
        Get all valid sources
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of valid sources
        """
        return self.get_by_validation_status("valid", skip, limit)
    
    def count_by_status(self, validation_status: str) -> int:
        """
        Count sources by validation status
        
        Args:
            validation_status: Validation status to count
            
        Returns:
            Total count
        """
        stmt = select(Source).where(Source.validation_status == validation_status)
        result = self.db.execute(stmt)
        return len(list(result.scalars().all()))
