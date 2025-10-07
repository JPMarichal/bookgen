"""
Notification SQLAlchemy model for logging sent notifications
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index, Boolean
from sqlalchemy.sql import func

from src.database.base import Base


class Notification(Base):
    """
    Notification model - logs all notifications sent by the system
    """
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Notification type and delivery method
    notification_type = Column(
        String(50),
        nullable=False,
        index=True
    )  # progress_update, completion, error_alert, status_change, admin_alert
    
    delivery_method = Column(
        String(50),
        nullable=False,
        index=True
    )  # websocket, webhook, email
    
    # Recipient information
    recipient = Column(String(255), nullable=False)  # email, user_id, webhook_url, etc.
    
    # Notification content
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    
    # Delivery status
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True
    )  # pending, delivered, failed, rate_limited
    
    delivery_attempts = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    
    # Related entity (job_id, biography_id, etc.)
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(Integer, nullable=True)
    
    # Metadata (renamed from metadata to avoid SQLAlchemy conflict)
    notification_metadata = Column(JSON, nullable=True)
    
    # Rate limiting flag
    is_rate_limited = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_notification_type_created', 'notification_type', 'created_at'),
        Index('idx_notification_status_created', 'status', 'created_at'),
        Index('idx_notification_recipient', 'recipient'),
        Index('idx_notification_entity', 'related_entity_type', 'related_entity_id'),
    )
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.notification_type}', method='{self.delivery_method}', status='{self.status}')>"
