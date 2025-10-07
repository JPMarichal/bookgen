"""
Example integration of notification system with biography generation
"""
import asyncio
from src.services.notifications import NotificationService


async def example_biography_generation_with_notifications():
    """
    Example showing how to integrate notifications into biography generation workflow
    """
    # Initialize notification service
    service = NotificationService()
    
    # Job details
    job_id = "example_job_123"
    biography_id = 999
    character_name = "Marie Curie"
    
    # Optional: configure webhook and email
    webhook_url = None  # Set to your webhook URL if available
    user_email = None   # Set to user's email if email is configured
    
    print(f"Starting biography generation for: {character_name}")
    print(f"Job ID: {job_id}")
    print()
    
    try:
        # Phase 1: Initialization
        print("📢 Phase 1: Initialization")
        await service.send_progress_update(
            job_id=job_id,
            progress=0,
            phase="Initializing biography generation",
            message=f"Starting generation for {character_name}",
            webhook_url=webhook_url
        )
        await asyncio.sleep(0.5)
        
        # Phase 2: Research
        print("📢 Phase 2: Research")
        await service.send_progress_update(
            job_id=job_id,
            progress=20,
            phase="Researching sources",
            message="Gathering biographical information",
            webhook_url=webhook_url
        )
        await asyncio.sleep(0.5)
        
        # Phase 3: Content Generation
        print("📢 Phase 3: Content Generation")
        for chapter in range(1, 6):
            progress = 20 + (chapter * 12)
            await service.send_progress_update(
                job_id=job_id,
                progress=progress,
                phase=f"Generating chapter {chapter} of 5",
                message=f"Creating content for chapter {chapter}",
                webhook_url=webhook_url
            )
            await asyncio.sleep(0.3)
        
        # Phase 4: Finalization
        print("📢 Phase 4: Finalization")
        await service.send_progress_update(
            job_id=job_id,
            progress=95,
            phase="Finalizing biography",
            message="Formatting and preparing output",
            webhook_url=webhook_url
        )
        await asyncio.sleep(0.5)
        
        # Completion
        print("📢 Completion")
        await service.send_completion_notification(
            job_id=job_id,
            biography_id=biography_id,
            character_name=character_name,
            status="completed",
            webhook_url=webhook_url,
            user_email=user_email,
            metadata={
                "chapters": 5,
                "total_words": 10000,
                "generation_time": 45.2
            }
        )
        
        print()
        print(f"✅ Biography generation completed successfully!")
        print(f"   Delivery status: {service.get_delivery_status()}")
        
    except Exception as e:
        # Error handling with notifications
        print(f"❌ Error occurred: {e}")
        
        await service.send_error_alert(
            job_id=job_id,
            error=str(e),
            severity="critical",
            webhook_url=webhook_url
        )
        
        raise
    
    finally:
        # Cleanup
        await service.close()


async def example_with_webhook():
    """
    Example showing webhook integration
    
    To test with a real webhook, use a service like:
    - https://webhook.site (get a free test URL)
    - https://requestbin.com
    """
    service = NotificationService()
    
    # Get a test webhook URL from https://webhook.site
    test_webhook_url = "https://webhook.site/your-unique-id"
    
    print(f"Sending test notifications to webhook: {test_webhook_url}")
    print("Check the webhook.site page to see the payloads")
    print()
    
    # Send various notification types
    await service.send_progress_update(
        job_id="test_123",
        progress=50,
        phase="Testing webhook",
        webhook_url=test_webhook_url
    )
    
    await service.send_completion_notification(
        job_id="test_123",
        biography_id=123,
        character_name="Test Character",
        webhook_url=test_webhook_url
    )
    
    await service.close()
    print("✅ Webhook notifications sent!")


async def example_websocket_monitoring():
    """
    Example showing how to monitor a job via WebSocket
    
    In a real application:
    1. Backend sends notifications via NotificationService
    2. Frontend connects to WebSocket endpoint
    3. Real-time updates are displayed to user
    """
    service = NotificationService()
    job_id = "monitored_job_456"
    
    # Get WebSocket manager
    ws_manager = service.get_websocket_client()
    
    print(f"WebSocket Example - Job {job_id}")
    print()
    print("In your frontend application, connect to:")
    print(f"  ws://localhost:8000/ws/notifications?job_id={job_id}")
    print()
    print("Then, when you send updates:")
    
    # Simulate sending updates
    await service.send_progress_update(
        job_id=job_id,
        progress=25,
        phase="Processing chapter 5"
    )
    
    await service.send_progress_update(
        job_id=job_id,
        progress=50,
        phase="Processing chapter 10"
    )
    
    await service.send_completion_notification(
        job_id=job_id,
        biography_id=789,
        character_name="WebSocket Test"
    )
    
    # Get connection stats
    stats = ws_manager.get_connection_count()
    print(f"Current WebSocket connections: {stats}")
    
    await service.close()


if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("BookGen Notification System - Integration Examples")
    print("=" * 80)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--webhook":
        print("Running webhook example...")
        print("Note: Replace the webhook URL with your own from webhook.site")
        print()
        # asyncio.run(example_with_webhook())
        print("⚠️  Skipped - configure webhook URL first")
    elif len(sys.argv) > 1 and sys.argv[1] == "--websocket":
        print("Running WebSocket example...")
        print()
        asyncio.run(example_websocket_monitoring())
    else:
        print("Running full biography generation example...")
        print()
        asyncio.run(example_biography_generation_with_notifications())
    
    print()
    print("=" * 80)
    print("Examples:")
    print("  python example_notification_integration.py              # Full generation")
    print("  python example_notification_integration.py --webhook    # Webhook test")
    print("  python example_notification_integration.py --websocket  # WebSocket test")
    print("=" * 80)
