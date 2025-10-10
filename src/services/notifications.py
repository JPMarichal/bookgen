"""
Comprehensive notification service integrating WebSocket, Webhook, and Email
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import os
from collections import defaultdict
import time

from src.websocket.manager import ConnectionManager, get_websocket_client
from src.webhooks.client import WebhookClient
from src.mailer.sender import EmailSender
from src.database.config import SessionLocal
from src.models.notification import Notification

logger = logging.getLogger(__name__)


class NotificationRateLimiter:
    """
    Rate limiter for notifications to prevent spam
    """
    
    def __init__(self, max_per_minute: int = 60, max_per_hour: int = 500):
        """
        Initialize rate limiter
        
        Args:
            max_per_minute: Maximum notifications per minute per recipient
            max_per_hour: Maximum notifications per hour per recipient
        """
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        
        # Track timestamps: {recipient: [timestamp1, timestamp2, ...]}
        self.timestamps: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, recipient: str) -> tuple[bool, Optional[str]]:
        """
        Check if notification is allowed for recipient
        
        Args:
            recipient: Recipient identifier
        
        Returns:
            Tuple of (allowed: bool, reason: Optional[str])
        """
        now = time.time()
        
        # Clean old timestamps
        self.timestamps[recipient] = [
            ts for ts in self.timestamps[recipient]
            if now - ts < 3600  # Keep last hour
        ]
        
        # Check per-minute limit
        recent_minute = [ts for ts in self.timestamps[recipient] if now - ts < 60]
        if len(recent_minute) >= self.max_per_minute:
            return False, f"Rate limit exceeded: {self.max_per_minute} notifications per minute"
        
        # Check per-hour limit
        if len(self.timestamps[recipient]) >= self.max_per_hour:
            return False, f"Rate limit exceeded: {self.max_per_hour} notifications per hour"
        
        # Add current timestamp
        self.timestamps[recipient].append(now)
        return True, None


class NotificationService:
    """
    Main notification service coordinating all notification channels
    """
    
    def __init__(
        self,
        websocket_manager: Optional[ConnectionManager] = None,
        webhook_client: Optional[WebhookClient] = None,
        email_sender: Optional[EmailSender] = None,
        rate_limiter: Optional[NotificationRateLimiter] = None,
        enable_logging: bool = True
    ):
        """
        Initialize notification service
        
        Args:
            websocket_manager: WebSocket connection manager
            webhook_client: Webhook client
            email_sender: Email sender
            rate_limiter: Rate limiter instance
            enable_logging: Whether to log notifications to database
        """
        self.websocket_manager = websocket_manager or get_websocket_client()
        self.webhook_client = webhook_client or WebhookClient()
        self.email_sender = email_sender or EmailSender()
        self.rate_limiter = rate_limiter or NotificationRateLimiter()
        self.enable_logging = enable_logging
        
        # Track last delivery status
        self.last_delivery_status = "UNKNOWN"
        
        logger.info("NotificationService initialized")
    
    def _log_notification(
        self,
        notification_type: str,
        delivery_method: str,
        recipient: str,
        message: str,
        status: str,
        subject: Optional[str] = None,
        error_message: Optional[str] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_rate_limited: bool = False
    ):
        """
        Log notification to database
        
        Args:
            notification_type: Type of notification
            delivery_method: Delivery method (websocket, webhook, email)
            recipient: Recipient identifier
            message: Notification message
            status: Delivery status
            subject: Optional subject
            error_message: Optional error message
            related_entity_type: Related entity type
            related_entity_id: Related entity ID
            metadata: Optional metadata
            is_rate_limited: Whether notification was rate limited
        """
        if not self.enable_logging:
            return
        
        try:
            db = SessionLocal()
            notification = Notification(
                notification_type=notification_type,
                delivery_method=delivery_method,
                recipient=recipient,
                subject=subject,
                message=message,
                status=status,
                error_message=error_message,
                related_entity_type=related_entity_type,
                related_entity_id=related_entity_id,
                notification_metadata=metadata,
                is_rate_limited=is_rate_limited,
                delivery_attempts=1,
                delivered_at=datetime.now(timezone.utc) if status == "delivered" else None
            )
            db.add(notification)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to log notification: {e}", exc_info=True)
    
    async def send_progress_update(
        self,
        job_id: str,
        progress: float,
        phase: str,
        message: Optional[str] = None,
        webhook_url: Optional[str] = None
    ):
        """
        Send progress update via WebSocket and optionally webhook
        
        Args:
            job_id: Job identifier
            progress: Progress percentage (0-100)
            phase: Current phase description
            message: Optional additional message
            webhook_url: Optional webhook URL for external notification
        """
        # Send via WebSocket (real-time, no rate limiting)
        try:
            await self.websocket_manager.send_progress_update(job_id, progress, phase, message)
            self._log_notification(
                notification_type="progress_update",
                delivery_method="websocket",
                recipient=job_id,
                message=f"{phase}: {progress}%",
                status="delivered",
                related_entity_type="job",
                related_entity_id=int(job_id) if job_id.isdigit() else None,
                metadata={"progress": progress, "phase": phase, "message": message}
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket progress update: {e}")
        
        # Send via webhook if provided
        if webhook_url:
            # Check rate limit for webhook
            allowed, reason = self.rate_limiter.is_allowed(webhook_url)
            if not allowed:
                logger.warning(f"Webhook rate limited for {webhook_url}: {reason}")
                self._log_notification(
                    notification_type="progress_update",
                    delivery_method="webhook",
                    recipient=webhook_url,
                    message=f"{phase}: {progress}%",
                    status="rate_limited",
                    error_message=reason,
                    is_rate_limited=True
                )
                return
            
            try:
                success, error = await self.webhook_client.send_progress_update(
                    webhook_url, job_id, progress, phase, message
                )
                self._log_notification(
                    notification_type="progress_update",
                    delivery_method="webhook",
                    recipient=webhook_url,
                    message=f"{phase}: {progress}%",
                    status="delivered" if success else "failed",
                    error_message=error,
                    related_entity_type="job",
                    related_entity_id=int(job_id) if job_id.isdigit() else None
                )
            except Exception as e:
                logger.error(f"Failed to send webhook progress update: {e}")
    
    async def send_completion_notification(
        self,
        job_id: str,
        biography_id: int,
        character_name: str = "Unknown",
        status: str = "completed",
        webhook_url: Optional[str] = None,
        user_email: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send completion notification via all configured channels
        
        Args:
            job_id: Job identifier
            biography_id: Biography ID
            character_name: Character name
            status: Job status
            webhook_url: Optional webhook URL
            user_email: Optional user email
            metadata: Optional additional metadata
        """
        success = True
        
        # Send via WebSocket
        try:
            await self.websocket_manager.send_completion_notification(
                job_id, biography_id, success=(status == "completed")
            )
            self._log_notification(
                notification_type="completion",
                delivery_method="websocket",
                recipient=job_id,
                message=f"Biography {biography_id} {status}",
                status="delivered",
                related_entity_type="biography",
                related_entity_id=biography_id,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket completion: {e}")
            success = False
        
        # Send via webhook if provided
        if webhook_url:
            allowed, reason = self.rate_limiter.is_allowed(webhook_url)
            if allowed:
                try:
                    webhook_success, error = await self.webhook_client.send_completion_notification(
                        webhook_url, job_id, biography_id, status, metadata
                    )
                    self._log_notification(
                        notification_type="completion",
                        delivery_method="webhook",
                        recipient=webhook_url,
                        message=f"Biography {biography_id} {status}",
                        status="delivered" if webhook_success else "failed",
                        error_message=error,
                        related_entity_type="biography",
                        related_entity_id=biography_id
                    )
                    if webhook_success:
                        self.last_delivery_status = "DELIVERED"
                except Exception as e:
                    logger.error(f"Failed to send webhook completion: {e}")
                    success = False
            else:
                self._log_notification(
                    notification_type="completion",
                    delivery_method="webhook",
                    recipient=webhook_url,
                    message=f"Biography {biography_id} {status}",
                    status="rate_limited",
                    error_message=reason,
                    is_rate_limited=True
                )
        
        # Send via email if provided
        if user_email:
            allowed, reason = self.rate_limiter.is_allowed(user_email)
            if allowed:
                try:
                    email_success, error = self.email_sender.send_completion_notification(
                        user_email, job_id, biography_id, character_name, status
                    )
                    self._log_notification(
                        notification_type="completion",
                        delivery_method="email",
                        recipient=user_email,
                        message=f"Biography {biography_id} {status}",
                        status="delivered" if email_success else "failed",
                        error_message=error,
                        related_entity_type="biography",
                        related_entity_id=biography_id
                    )
                except Exception as e:
                    logger.error(f"Failed to send email completion: {e}")
                    success = False
            else:
                self._log_notification(
                    notification_type="completion",
                    delivery_method="email",
                    recipient=user_email,
                    message=f"Biography {biography_id} {status}",
                    status="rate_limited",
                    error_message=reason,
                    is_rate_limited=True
                )
        
        if success:
            self.last_delivery_status = "DELIVERED"
    
    async def send_error_alert(
        self,
        job_id: str,
        error: str,
        severity: str = "error",
        webhook_url: Optional[str] = None,
        admin_emails: Optional[List[str]] = None
    ):
        """
        Send error alert notifications
        
        Args:
            job_id: Job identifier
            error: Error message
            severity: Error severity (error, warning, critical)
            webhook_url: Optional webhook URL
            admin_emails: Optional list of admin emails
        """
        # Send via WebSocket
        try:
            await self.websocket_manager.send_error_alert(job_id, error, severity)
            self._log_notification(
                notification_type="error_alert",
                delivery_method="websocket",
                recipient=job_id,
                message=error,
                status="delivered",
                related_entity_type="job",
                related_entity_id=int(job_id) if job_id.isdigit() else None,
                metadata={"severity": severity}
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket error alert: {e}")
        
        # Send via webhook if provided
        if webhook_url:
            allowed, reason = self.rate_limiter.is_allowed(webhook_url)
            if allowed:
                try:
                    await self.webhook_client.send_error_alert(webhook_url, job_id, error, severity)
                    self._log_notification(
                        notification_type="error_alert",
                        delivery_method="webhook",
                        recipient=webhook_url,
                        message=error,
                        status="delivered",
                        metadata={"severity": severity}
                    )
                except Exception as e:
                    logger.error(f"Failed to send webhook error alert: {e}")
        
        # Send to admin emails if critical and emails provided
        if severity == "critical" and admin_emails:
            for email in admin_emails:
                allowed, reason = self.rate_limiter.is_allowed(email)
                if allowed:
                    try:
                        self.email_sender.send_error_alert(email, job_id, error, severity)
                        self._log_notification(
                            notification_type="error_alert",
                            delivery_method="email",
                            recipient=email,
                            message=error,
                            status="delivered",
                            metadata={"severity": severity}
                        )
                    except Exception as e:
                        logger.error(f"Failed to send admin email alert: {e}")
    
    async def send_admin_alert(
        self,
        alert_type: str,
        message: str,
        admin_emails: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Send alert to administrators
        
        Args:
            alert_type: Type of alert
            message: Alert message
            admin_emails: List of admin email addresses
            metadata: Optional metadata
        """
        if not admin_emails:
            logger.warning("No admin emails configured for admin alert")
            return
        
        results = self.email_sender.send_admin_alert(admin_emails, alert_type, message, metadata)
        
        for email, success, error in results:
            self._log_notification(
                notification_type="admin_alert",
                delivery_method="email",
                recipient=email,
                message=message,
                subject=f"Admin Alert: {alert_type}",
                status="delivered" if success else "failed",
                error_message=error,
                metadata=metadata
            )
    
    def get_delivery_status(self) -> str:
        """
        Get last delivery status
        
        Returns:
            Last delivery status
        """
        return self.last_delivery_status
    
    def get_websocket_client(self) -> ConnectionManager:
        """
        Get WebSocket connection manager
        
        Returns:
            ConnectionManager instance
        """
        return self.websocket_manager
    
    async def close(self):
        """Close all connections"""
        await self.webhook_client.close()
