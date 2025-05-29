import json
import hmac
import hashlib
import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from app.tasks.webhook_tasks import celery_app # Import the Celery app instance
from app.config import settings # Import settings for Celery broker/backend

# Assuming these will be configured globally or passed via dependency injection
WEBHOOK_SECRET_KEY = "your_super_secret_webhook_key" # This should be a strong, securely generated key
REDIS_PUBSUB_CHANNEL = "realtime_events" # Redis channel for WebSocket broadcasting

class EventPublisher:
    def __init__(self, webhook_service: Any, redis_client: Any):
        self.webhook_service = webhook_service
        self.redis_client = redis_client

    async def publish(self, event_type: str, payload: Dict[str, Any], is_realtime: bool = False):
        """
        Publishes an event to appropriate subscribers.
        If is_realtime is True, publishes to WebSocket (Redis Pub/Sub).
        Always dispatches to HTTP webhooks if subscribed.
        """
        event_data = {
            "event_type": event_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": payload
        }

        # 1. Dispatch to HTTP Webhooks (via Celery)
        subscribed_webhooks = await self.webhook_service.list_webhooks(event_type=event_type, is_active=True)
        for webhook in subscribed_webhooks:
            celery_app.send_task(
                'app.tasks.webhook_tasks.send_webhook_task', # Full path to the task
                args=[webhook.target_url, event_data, webhook.secret, webhook.headers]
            )
            print(f"Dispatched HTTP webhook for event '{event_type}' to {webhook.target_url} via Celery")

        # 2. Publish to Real-time WebSocket (Redis Pub/Sub)
        if is_realtime and self.redis_client:
            try:
                await self.redis_client.publish(REDIS_PUBSUB_CHANNEL, json.dumps(event_data))
                print(f"Published real-time event '{event_type}' to Redis Pub/Sub channel '{REDIS_PUBSUB_CHANNEL}'")
            except Exception as e:
                print(f"Failed to publish real-time event to Redis: {e}")

# Example usage (for testing/demonstration, not for production initialization)
# from app.adapters.redis_adapter import RedisAdapter
# from app.services.webhook_service import WebhookService
# from app.adapters.mongodb_adapter import MongoDBAdapter
# from app.config import settings
#
# # Assuming Redis and MongoDB adapters are initialized elsewhere
# redis_adapter = RedisAdapter(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
# mongodb_adapter = MongoDBAdapter(connection_string=settings.MONGODB_CONNECTION_STRING, database_name=settings.MONGODB_DATABASE_NAME)
# webhook_service_instance = WebhookService(storage_adapter=mongodb_adapter)
#
# event_publisher = EventPublisher(webhook_service=webhook_service_instance, redis_client=redis_adapter.client)