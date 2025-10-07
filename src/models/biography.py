"""
Biography SQLAlchemy model
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from src.database.base import Base


class Biography(Base):
    """
    Biography model - represents a biography generation project
    """
    __tablename__ = "biographies"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core fields
    character_name = Column(String(200), nullable=False, index=True)
    status = Column(
        String(50), 
        nullable=False, 
        default="pending",
        index=True
    )  # pending, in_progress, completed, failed
    
    # Metadata (use bio_metadata to avoid SQLAlchemy reserved name)
    bio_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Relationships
    chapters = relationship("Chapter", back_populates="biography", cascade="all, delete-orphan")
    generation_jobs = relationship("GenerationJob", back_populates="biography", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_biography_status_created', 'status', 'created_at'),
        Index('idx_biography_character_status', 'character_name', 'status'),
    )
    
    def __repr__(self):
        return f"<Biography(id={self.id}, character_name='{self.character_name}', status='{self.status}')>"
