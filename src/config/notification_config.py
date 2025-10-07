"""
Notification system configuration
"""
import os
from typing import List, Optional


class NotificationConfig:
    """Configuration for notification system"""
    
    # WebSocket configuration
    WEBSOCKET_ENABLED: bool = os.getenv("WEBSOCKET_ENABLED", "true").lower() == "true"
    
    # Webhook configuration
    WEBHOOK_TIMEOUT: int = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
    WEBHOOK_MAX_RETRIES: int = int(os.getenv("WEBHOOK_MAX_RETRIES", "3"))
    
    # Email configuration
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@bookgen.com")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    
    # Admin emails for alerts
    ADMIN_EMAILS: List[str] = [
        email.strip()
        for email in os.getenv("ADMIN_EMAILS", "").split(",")
        if email.strip()
    ]
    
    # Rate limiting
    NOTIFICATION_RATE_LIMIT_PER_MINUTE: int = int(
        os.getenv("NOTIFICATION_RATE_LIMIT_PER_MINUTE", "60")
    )
    NOTIFICATION_RATE_LIMIT_PER_HOUR: int = int(
        os.getenv("NOTIFICATION_RATE_LIMIT_PER_HOUR", "500")
    )
    
    # Notification logging
    ENABLE_NOTIFICATION_LOGGING: bool = os.getenv(
        "ENABLE_NOTIFICATION_LOGGING", "true"
    ).lower() == "true"
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """
        Get configuration summary
        
        Returns:
            Dictionary with current configuration
        """
        return {
            "websocket": {
                "enabled": cls.WEBSOCKET_ENABLED,
            },
            "webhook": {
                "timeout": cls.WEBHOOK_TIMEOUT,
                "max_retries": cls.WEBHOOK_MAX_RETRIES,
            },
            "email": {
                "enabled": cls.EMAIL_ENABLED,
                "smtp_configured": bool(cls.SMTP_HOST and cls.SMTP_USER),
                "from_email": cls.FROM_EMAIL,
                "admin_count": len(cls.ADMIN_EMAILS),
            },
            "rate_limiting": {
                "per_minute": cls.NOTIFICATION_RATE_LIMIT_PER_MINUTE,
                "per_hour": cls.NOTIFICATION_RATE_LIMIT_PER_HOUR,
            },
            "logging": {
                "enabled": cls.ENABLE_NOTIFICATION_LOGGING,
            }
        }


# Export configuration instance
notification_config = NotificationConfig()
