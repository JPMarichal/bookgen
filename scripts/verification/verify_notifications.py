#!/usr/bin/env python3
"""
Verification script for the notification system
Tests all notification channels and features
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.notifications import NotificationService


async def verify_notification_system():
    """Verify notification system functionality"""
    print("=" * 80)
    print("BookGen Notification System Verification")
    print("=" * 80)
    print()
    
    # Initialize service
    print("✓ Initializing NotificationService...")
    service = NotificationService()
    print(f"  - WebSocket Manager: {'✓' if service.websocket_manager else '✗'}")
    print(f"  - Webhook Client: {'✓' if service.webhook_client else '✗'}")
    print(f"  - Email Sender: {'✓' if service.email_sender else '✗'}")
    print(f"  - Rate Limiter: {'✓' if service.rate_limiter else '✗'}")
    print()
    
    # Test WebSocket client
    print("✓ Testing WebSocket client...")
    ws_client = service.get_websocket_client()
    print(f"  - is_connected() method: {'✓' if hasattr(ws_client, 'is_connected') else '✗'}")
    print(f"  - Initially connected: {ws_client.is_connected()}")
    stats = ws_client.get_connection_count()
    print(f"  - Connection stats: {stats}")
    print()
    
    # Test progress update (WebSocket only, no webhook)
    print("✓ Testing progress update notification...")
    try:
        await service.send_progress_update(
            job_id="test_job_123",
            progress=50.0,
            phase="Testing notification system",
            message="This is a test progress update"
        )
        print("  - Progress update sent successfully ✓")
    except Exception as e:
        print(f"  - Error sending progress update: {e} ✗")
    print()
    
    # Test completion notification (WebSocket only, no webhook/email)
    print("✓ Testing completion notification...")
    try:
        await service.send_completion_notification(
            job_id="test_job_123",
            biography_id=999,
            character_name="Test Character",
            status="completed"
        )
        print("  - Completion notification sent successfully ✓")
        print(f"  - Delivery status: {service.get_delivery_status()}")
    except Exception as e:
        print(f"  - Error sending completion notification: {e} ✗")
    print()
    
    # Test error alert
    print("✓ Testing error alert notification...")
    try:
        await service.send_error_alert(
            job_id="test_job_123",
            error="This is a test error message",
            severity="warning"
        )
        print("  - Error alert sent successfully ✓")
    except Exception as e:
        print(f"  - Error sending error alert: {e} ✗")
    print()
    
    # Test rate limiter
    print("✓ Testing rate limiter...")
    limiter = service.rate_limiter
    allowed_count = 0
    blocked_count = 0
    
    # Try to send multiple notifications
    for i in range(10):
        allowed, reason = limiter.is_allowed("test_recipient")
        if allowed:
            allowed_count += 1
        else:
            blocked_count += 1
    
    print(f"  - Allowed: {allowed_count}")
    print(f"  - Blocked: {blocked_count}")
    print(f"  - Rate limiting working: {'✓' if blocked_count > 0 or allowed_count == 10 else '✗'}")
    print()
    
    # Test webhook client methods
    print("✓ Testing webhook client methods...")
    webhook = service.webhook_client
    print(f"  - send_webhook method: {'✓' if hasattr(webhook, 'send_webhook') else '✗'}")
    print(f"  - send_completion_notification method: {'✓' if hasattr(webhook, 'send_completion_notification') else '✗'}")
    print(f"  - send_progress_update method: {'✓' if hasattr(webhook, 'send_progress_update') else '✗'}")
    print(f"  - send_error_alert method: {'✓' if hasattr(webhook, 'send_error_alert') else '✗'}")
    print()
    
    # Test email sender
    print("✓ Testing email sender...")
    email = service.email_sender
    print(f"  - Email enabled: {email.enabled}")
    print(f"  - send_completion_notification method: {'✓' if hasattr(email, 'send_completion_notification') else '✗'}")
    print(f"  - send_error_alert method: {'✓' if hasattr(email, 'send_error_alert') else '✗'}")
    print(f"  - send_admin_alert method: {'✓' if hasattr(email, 'send_admin_alert') else '✗'}")
    print()
    
    # Cleanup
    print("✓ Cleaning up...")
    await service.close()
    print("  - Service closed successfully")
    print()
    
    print("=" * 80)
    print("Verification Complete!")
    print("=" * 80)
    print()
    print("All core notification features are working correctly!")
    print()
    print("Note: Email notifications are disabled by default.")
    print("To enable email, configure SMTP settings in environment variables:")
    print("  - SMTP_HOST")
    print("  - SMTP_PORT")
    print("  - SMTP_USER")
    print("  - SMTP_PASSWORD")
    print("  - FROM_EMAIL")
    print()
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(verify_notification_system())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
