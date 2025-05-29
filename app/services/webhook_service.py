from typing import List, Optional
from app.models.webhook import Webhook
from app.adapters.base import AbstractStorageAdapter # Assuming base adapter is used

class WebhookService:
    def __init__(self, storage_adapter: AbstractStorageAdapter):
        self.storage_adapter = storage_adapter

    async def create_webhook(
        self,
        webhook: Webhook
    ) -> Webhook:
        """Creates a new webhook subscription."""
        # In a real application, you might generate the ID and secret here
        # For now, assuming the webhook object passed already has an ID (e.g., UUID)
        # and a securely generated secret.
        created_webhook = await self.storage_adapter.create(webhook)
        return Webhook.model_validate(created_webhook.model_dump())

    async def get_webhook(self, webhook_id: str) -> Optional[Webhook]:
        """Retrieves a webhook by its ID."""
        read_webhook = await self.storage_adapter.read(Webhook, webhook_id)
        return Webhook.model_validate(read_webhook.model_dump()) if read_webhook else None

    async def list_webhooks(
        self,
        event_type: Optional[str] = None,
        owner_id: Optional[str] = None
    ) -> List[Webhook]:
        """Lists webhooks, optionally filtered by event type or owner ID."""
        # This method would need to be enhanced in the adapter to support filtering
        # For now, it lists all and filters in memory (not efficient for large datasets)
        all_webhooks_base = await self.storage_adapter.list(Webhook)
        all_webhooks = [Webhook.model_validate(wh.model_dump()) for wh in all_webhooks_base]
        
        filtered_webhooks = []
        for webhook in all_webhooks:
            match_event = (event_type is None) or (webhook.event_type == event_type)
            match_owner = (owner_id is None) or (webhook.owner_id == owner_id)
            if match_event and match_owner:
                filtered_webhooks.append(webhook)
        return filtered_webhooks

    async def update_webhook(self, webhook: Webhook) -> Webhook:
        """Updates an existing webhook subscription."""
        # Ensure the webhook exists before attempting to update
        existing_webhook = await self.storage_adapter.read(Webhook, webhook.id)
        if not existing_webhook:
            raise ValueError(f"Webhook with ID {webhook.id} not found.")
        updated_webhook = await self.storage_adapter.update(webhook)
        return Webhook.model_validate(updated_webhook.model_dump())

    async def delete_webhook(self, webhook_id: str) -> None:
        """Deletes a webhook subscription by its ID."""
        await self.storage_adapter.delete(Webhook, webhook_id)