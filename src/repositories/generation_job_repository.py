"""
GenerationJob repository
"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.models.generation_job import GenerationJob
from .base import BaseRepository


class GenerationJobRepository(BaseRepository[GenerationJob]):
    """
    Repository for GenerationJob model with specific queries
    """
    
    def __init__(self, db: Session):
        super().__init__(GenerationJob, db)
    
    def get_by_biography(self, biography_id: int) -> List[GenerationJob]:
        """
        Get all jobs for a biography
        
        Args:
            biography_id: Biography ID
            
        Returns:
            List of jobs ordered by creation date descending
        """
        stmt = (
            select(GenerationJob)
            .where(GenerationJob.biography_id == biography_id)
            .order_by(GenerationJob.created_at.desc())
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[GenerationJob]:
        """
        Get jobs by status
        
        Args:
            status: Status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of jobs
        """
        stmt = (
            select(GenerationJob)
            .where(GenerationJob.status == status)
            .order_by(GenerationJob.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_active_jobs(self) -> List[GenerationJob]:
        """
        Get all active (pending or running) jobs
        
        Returns:
            List of active jobs
        """
        stmt = (
            select(GenerationJob)
            .where(GenerationJob.status.in_(["pending", "running"]))
            .order_by(GenerationJob.created_at)
        )
        result = self.db.execute(stmt)
        return list(result.scalars().all())
    
    def get_latest_by_biography(self, biography_id: int) -> Optional[GenerationJob]:
        """
        Get the latest job for a biography
        
        Args:
            biography_id: Biography ID
            
        Returns:
            Latest job or None if no jobs exist
        """
        stmt = (
            select(GenerationJob)
            .where(GenerationJob.biography_id == biography_id)
            .order_by(GenerationJob.created_at.desc())
            .limit(1)
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def get_with_biography(self, id: int) -> Optional[GenerationJob]:
        """
        Get job by ID with biography eagerly loaded
        
        Args:
            id: Job ID
            
        Returns:
            Job with biography or None if not found
        """
        stmt = (
            select(GenerationJob)
            .where(GenerationJob.id == id)
            .options(joinedload(GenerationJob.biography))
        )
        result = self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
