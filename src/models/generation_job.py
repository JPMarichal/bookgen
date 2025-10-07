"""
GenerationJob SQLAlchemy model
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database.base import Base


class GenerationJob(Base):
    """
    GenerationJob model - represents a background job for biography generation
    """
    __tablename__ = "generation_jobs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    biography_id = Column(Integer, ForeignKey("biographies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Core fields
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )  # pending, running, completed, failed, paused
    
    # Progress tracking
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 to 100.0
    current_phase = Column(String(100), nullable=True)
    
    # Logs and error tracking
    logs = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Additional metadata
    job_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    biography = relationship("Biography", back_populates="generation_jobs")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_job_status_created', 'status', 'created_at'),
        Index('idx_job_biography_status', 'biography_id', 'status'),
    )
    
    def __repr__(self):
        return f"<GenerationJob(id={self.id}, biography_id={self.biography_id}, status='{self.status}', progress={self.progress})>"
