"""
Tests for the notification system
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio
from datetime import datetime, timezone

from src.services.notifications import NotificationService, NotificationRateLimiter
from src.websocket.manager import ConnectionManager
from src.webhooks.client import WebhookClient
from src.email.sender import EmailSender


class TestNotificationRateLimiter:
    """Tests for NotificationRateLimiter"""
    
    def test_rate_limiter_allows_within_limit(self):
        """Test that rate limiter allows requests within limits"""
        limiter = NotificationRateLimiter(max_per_minute=5, max_per_hour=10)
        
        # Should allow first 5 requests
        for _ in range(5):
            allowed, reason = limiter.is_allowed("test@example.com")
            assert allowed is True
            assert reason is None
    
    def test_rate_limiter_blocks_over_minute_limit(self):
        """Test that rate limiter blocks when per-minute limit exceeded"""
        limiter = NotificationRateLimiter(max_per_minute=2, max_per_hour=10)
        
        # First 2 should be allowed
        for _ in range(2):
            allowed, reason = limiter.is_allowed("test@example.com")
            assert allowed is True
        
        # Third should be blocked
        allowed, reason = limiter.is_allowed("test@example.com")
        assert allowed is False
        assert "per minute" in reason
    
    def test_rate_limiter_separate_recipients(self):
        """Test that rate limiter tracks recipients separately"""
        limiter = NotificationRateLimiter(max_per_minute=2, max_per_hour=10)
        
        # Different recipients should have independent limits
        allowed1, _ = limiter.is_allowed("test1@example.com")
        allowed2, _ = limiter.is_allowed("test2@example.com")
        
        assert allowed1 is True
        assert allowed2 is True


class TestConnectionManager:
    """Tests for WebSocket ConnectionManager"""
    
    @pytest.mark.asyncio
    async def test_connection_manager_connect(self):
        """Test WebSocket connection"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        await manager.connect(websocket, user_id="user1")
        
        assert websocket.accept.called
        assert "user1" in manager.active_connections
        assert websocket in manager.active_connections["user1"]
    
    def test_connection_manager_disconnect(self):
        """Test WebSocket disconnection"""
        manager = ConnectionManager()
        websocket = Mock()
        
        manager.active_connections["user1"] = {websocket}
        manager.disconnect(websocket, user_id="user1")
        
        assert "user1" not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_send_to_user(self):
        """Test sending message to user"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        manager.active_connections["user1"] = {websocket}
        
        message = {"type": "test", "data": "hello"}
        await manager.send_to_user(message, "user1")
        
        websocket.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_send_progress_update(self):
        """Test sending progress update"""
        manager = ConnectionManager()
        websocket = AsyncMock()
        
        manager.job_connections["job1"] = {websocket}
        
        await manager.send_progress_update("job1", 50.0, "Processing", "Test message")
        
        assert websocket.send_json.called
        call_args = websocket.send_json.call_args[0][0]
        assert call_args["type"] == "progress_update"
        assert call_args["job_id"] == "job1"
        assert call_args["progress"] == 50.0
        assert call_args["phase"] == "Processing"
    
    def test_is_connected(self):
        """Test connection status check"""
        manager = ConnectionManager()
        websocket = Mock()
        
        assert manager.is_connected(user_id="user1") is False
        
        manager.active_connections["user1"] = {websocket}
        assert manager.is_connected(user_id="user1") is True
    
    def test_get_connection_count(self):
        """Test getting connection statistics"""
        manager = ConnectionManager()
        ws1, ws2 = Mock(), Mock()
        
        manager.active_connections["user1"] = {ws1, ws2}
        manager.job_connections["job1"] = {ws1}
        
        stats = manager.get_connection_count()
        
        assert stats["total_users"] == 1
        assert stats["total_user_connections"] == 2
        assert stats["total_jobs"] == 1
        assert stats["total_job_connections"] == 1


class TestWebhookClient:
    """Tests for WebhookClient"""
    
    @pytest.mark.asyncio
    async def test_send_webhook_success(self):
        """Test successful webhook delivery"""
        client = WebhookClient()
        
        with patch.object(client.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "OK"
            mock_post.return_value = mock_response
            
            success, error = await client.send_webhook(
                "https://example.com/webhook",
                {"event": "test"}
            )
            
            assert success is True
            assert error is None
            assert mock_post.called
    
    @pytest.mark.asyncio
    async def test_send_webhook_failure(self):
        """Test webhook delivery failure"""
        client = WebhookClient(max_retries=0)
        
        with patch.object(client.client, 'post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Server Error"
            mock_post.return_value = mock_response
            
            success, error = await client.send_webhook(
                "https://example.com/webhook",
                {"event": "test"}
            )
            
            assert success is False
            assert error is not None
            assert "500" in error
    
    @pytest.mark.asyncio
    async def test_send_completion_notification(self):
        """Test sending completion webhook"""
        client = WebhookClient()
        
        with patch.object(client, 'send_webhook', return_value=(True, None)) as mock_send:
            success, error = await client.send_completion_notification(
                "https://example.com/webhook",
                "job123",
                456,
                "completed"
            )
            
            assert success is True
            assert mock_send.called
            
            # Check payload structure
            call_args = mock_send.call_args[0]
            payload = call_args[1]
            assert payload["event"] == "job.completed"
            assert payload["job_id"] == "job123"
            assert payload["biography_id"] == 456
            assert payload["status"] == "completed"


class TestEmailSender:
    """Tests for EmailSender"""
    
    def test_email_sender_disabled_by_default(self):
        """Test that email is disabled without configuration"""
        sender = EmailSender(
            smtp_host=None,
            smtp_user=None,
            smtp_password=None,
            enabled=None
        )
        
        assert sender.enabled is False
    
    def test_email_sender_enabled_with_config(self):
        """Test that email is enabled with configuration"""
        sender = EmailSender(
            smtp_host="smtp.example.com",
            smtp_user="user@example.com",
            smtp_password="password",
            enabled=True
        )
        
        assert sender.enabled is True
    
    def test_send_email_disabled(self):
        """Test sending email when disabled"""
        sender = EmailSender(enabled=False)
        
        success, error = sender._send_email(
            "to@example.com",
            "Test",
            "Test message"
        )
        
        assert success is False
        assert "disabled" in error
    
    @patch('smtplib.SMTP')
    def test_send_completion_notification(self, mock_smtp):
        """Test sending completion notification email"""
        sender = EmailSender(
            smtp_host="smtp.example.com",
            smtp_port=587,
            smtp_user="user@example.com",
            smtp_password="password",
            from_email="from@example.com",
            enabled=True
        )
        
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        success, error = sender.send_completion_notification(
            "to@example.com",
            "job123",
            456,
            "Albert Einstein",
            "completed"
        )
        
        assert success is True
        assert error is None
        assert mock_server.send_message.called


class TestNotificationService:
    """Tests for NotificationService"""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization"""
        service = NotificationService()
        
        assert service.websocket_manager is not None
        assert service.webhook_client is not None
        assert service.email_sender is not None
        assert service.rate_limiter is not None
    
    @pytest.mark.asyncio
    async def test_send_progress_update_websocket(self):
        """Test sending progress update via WebSocket"""
        mock_ws_manager = AsyncMock()
        service = NotificationService(
            websocket_manager=mock_ws_manager,
            enable_logging=False
        )
        
        await service.send_progress_update(
            "job123",
            50.0,
            "Processing chapter 3"
        )
        
        mock_ws_manager.send_progress_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_completion_notification_all_channels(self):
        """Test sending completion via all channels"""
        mock_ws_manager = AsyncMock()
        mock_webhook_client = AsyncMock()
        mock_webhook_client.send_completion_notification = AsyncMock(return_value=(True, None))
        mock_email_sender = Mock()
        mock_email_sender.send_completion_notification = Mock(return_value=(True, None))
        
        service = NotificationService(
            websocket_manager=mock_ws_manager,
            webhook_client=mock_webhook_client,
            email_sender=mock_email_sender,
            enable_logging=False
        )
        
        await service.send_completion_notification(
            job_id="job123",
            biography_id=456,
            character_name="Test Character",
            webhook_url="https://example.com/webhook",
            user_email="user@example.com"
        )
        
        # Verify all channels were called
        mock_ws_manager.send_completion_notification.assert_called_once()
        mock_webhook_client.send_completion_notification.assert_called_once()
        mock_email_sender.send_completion_notification.assert_called_once()
        
        # Verify delivery status
        assert service.get_delivery_status() == "DELIVERED"
    
    @pytest.mark.asyncio
    async def test_send_error_alert(self):
        """Test sending error alerts"""
        mock_ws_manager = AsyncMock()
        service = NotificationService(
            websocket_manager=mock_ws_manager,
            enable_logging=False
        )
        
        await service.send_error_alert(
            "job123",
            "Test error",
            "critical"
        )
        
        mock_ws_manager.send_error_alert.assert_called_once_with(
            "job123",
            "Test error",
            "critical"
        )
    
    @pytest.mark.asyncio
    async def test_rate_limiting_blocks_excess_notifications(self):
        """Test that rate limiting prevents spam"""
        mock_webhook_client = AsyncMock()
        mock_webhook_client.send_completion_notification = AsyncMock(return_value=(True, None))
        
        rate_limiter = NotificationRateLimiter(max_per_minute=1, max_per_hour=1)
        
        service = NotificationService(
            websocket_manager=AsyncMock(),
            webhook_client=mock_webhook_client,
            rate_limiter=rate_limiter,
            enable_logging=False
        )
        
        webhook_url = "https://example.com/webhook"
        
        # First notification should go through
        await service.send_completion_notification(
            job_id="job1",
            biography_id=1,
            webhook_url=webhook_url
        )
        
        # Second should be rate limited
        await service.send_completion_notification(
            job_id="job2",
            biography_id=2,
            webhook_url=webhook_url
        )
        
        # Webhook client should only be called once
        assert mock_webhook_client.send_completion_notification.call_count == 1
    
    def test_get_websocket_client(self):
        """Test getting WebSocket client"""
        service = NotificationService()
        client = service.get_websocket_client()
        
        assert isinstance(client, ConnectionManager)
    
    def test_get_delivery_status(self):
        """Test getting delivery status"""
        service = NotificationService()
        
        # Initially unknown
        assert service.get_delivery_status() == "UNKNOWN"


class TestNotificationIntegration:
    """Integration tests for notification system"""
    
    @pytest.mark.asyncio
    async def test_full_notification_flow(self):
        """Test complete notification flow"""
        # Create service with mocked dependencies
        mock_ws_manager = AsyncMock()
        mock_webhook_client = AsyncMock()
        mock_webhook_client.send_completion_notification = AsyncMock(return_value=(True, None))
        
        service = NotificationService(
            websocket_manager=mock_ws_manager,
            webhook_client=mock_webhook_client,
            enable_logging=False
        )
        
        # Simulate a job lifecycle
        job_id = "integration_test_job"
        biography_id = 999
        webhook_url = "https://example.com/webhook"
        
        # 1. Send progress updates
        await service.send_progress_update(job_id, 0, "Starting", webhook_url=webhook_url)
        await service.send_progress_update(job_id, 50, "Processing", webhook_url=webhook_url)
        await service.send_progress_update(job_id, 100, "Finalizing", webhook_url=webhook_url)
        
        # 2. Send completion
        await service.send_completion_notification(
            job_id=job_id,
            biography_id=biography_id,
            character_name="Test Character",
            status="completed",
            webhook_url=webhook_url
        )
        
        # Verify calls
        assert mock_ws_manager.send_progress_update.call_count == 3
        assert mock_webhook_client.send_progress_update.call_count == 3
        assert mock_webhook_client.send_completion_notification.call_count == 1
        assert service.get_delivery_status() == "DELIVERED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
