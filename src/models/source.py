"""
Source SQLAlchemy model
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Index
from sqlalchemy.sql import func

from src.database.base import Base


class Source(Base):
    """
    Source model - represents a research source for biography generation
    """
    __tablename__ = "sources"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core fields
    url = Column(String(2048), nullable=True, index=True)
    title = Column(String(500), nullable=False)
    author = Column(String(200), nullable=True)
    publication_date = Column(String(100), nullable=True)
    
    # Validation and scoring
    relevance_score = Column(Float, nullable=True)
    validation_status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )  # pending, valid, invalid, inaccessible
    
    # Additional metadata
    source_type = Column(String(50), nullable=True)  # url, book, article, document, other
    content_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_source_validation_relevance', 'validation_status', 'relevance_score'),
        Index('idx_source_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Source(id={self.id}, title='{self.title}', validation_status='{self.validation_status}')>"
