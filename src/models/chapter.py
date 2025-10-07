"""
Chapter SQLAlchemy model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.base import Base


class Chapter(Base):
    """
    Chapter model - represents a chapter in a biography
    """
    __tablename__ = "chapters"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    biography_id = Column(Integer, ForeignKey("biographies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Core fields
    number = Column(Integer, nullable=False)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    word_count = Column(Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    biography = relationship("Biography", back_populates="chapters")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_chapter_biography_number', 'biography_id', 'number', unique=True),
    )
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, biography_id={self.biography_id}, number={self.number}, word_count={self.word_count})>"
