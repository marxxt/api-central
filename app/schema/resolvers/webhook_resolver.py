import strawberry
from typing import List, Optional
from datetime import datetime # Import datetime
from app.models.webhook import Webhook
from app.services.webhook_service import WebhookService
from app.adapters.mongodb_adapter import MongoDBAdapter # Assuming MongoDB is the chosen adapter
from app.config import settings # Assuming settings contains DB connection info

# Initialize the storage adapter and service
# In a real application, this would likely be handled by a dependency injection system
mongodb_adapter = MongoDBAdapter(
    connection_string=settings.MONGODB_CONNECTION_STRING,
    database_name=settings.MONGODB_DATABASE_NAME
)
webhook_service = WebhookService(storage_adapter=mongodb_adapter)

@strawberry.type
class WebhookType:
    id: str
    target_url: str
    event_type: str
    is_active: bool
    owner_id: Optional[str]
    created_at: datetime # Use datetime directly
    updated_at: datetime # Use datetime directly

@strawberry.input
class CreateWebhookInput:
    id: str # Assuming ID is provided by the client or generated before this point
    target_url: str
    event_type: str
    secret: str
    owner_id: Optional[str] = None
    is_active: bool = True

@strawberry.input
class UpdateWebhookInput:
    id: str
    target_url: Optional[str] = None
    event_type: Optional[str] = None
    secret: Optional[str] = None
    owner_id: Optional[str] = None
    is_active: Optional[bool] = None

@strawberry.type
class WebhookQuery:
    @strawberry.field
    async def webhook(self, id: str) -> Optional[WebhookType]:
        """Retrieve a single webhook by ID."""
        webhook = await webhook_service.get_webhook(id)
        return WebhookType(**webhook.model_dump()) if webhook else None

    @strawberry.field
    async def webhooks(
        self,
        event_type: Optional[str] = None,
        owner_id: Optional[str] = None
    ) -> List[WebhookType]:
        """List all webhooks, with optional filtering."""
        webhooks = await webhook_service.list_webhooks(event_type, owner_id)
        return [WebhookType(**wh.model_dump()) for wh in webhooks]

@strawberry.type
class WebhookMutation:
    @strawberry.mutation
    async def create_webhook(self, input: CreateWebhookInput) -> WebhookType:
        """Create a new webhook subscription."""
        # Convert Strawberry input to Pydantic model
        new_webhook = Webhook(
            id=input.id,
            target_url=input.target_url,
            event_type=input.event_type,
            secret=input.secret,
            owner_id=input.owner_id,
            is_active=input.is_active,
            headers=None # Explicitly pass None for headers
        )
        created_webhook = await webhook_service.create_webhook(new_webhook)
        return WebhookType(**created_webhook.model_dump())

    @strawberry.mutation
    async def update_webhook(self, input: UpdateWebhookInput) -> WebhookType:
        """Update an existing webhook subscription."""
        # Fetch existing webhook to apply partial updates
        existing_webhook = await webhook_service.get_webhook(input.id)
        if not existing_webhook:
            raise ValueError(f"Webhook with ID {input.id} not found.")
        
        # Apply updates from input to the existing webhook model
        if input.target_url is not None:
            existing_webhook.target_url = input.target_url
        if input.event_type is not None:
            existing_webhook.event_type = input.event_type
        if input.secret is not None:
            existing_webhook.secret = input.secret
        if input.owner_id is not None:
            existing_webhook.owner_id = input.owner_id
        if input.is_active is not None:
            existing_webhook.is_active = input.is_active
            
        updated_webhook = await webhook_service.update_webhook(existing_webhook)
        return WebhookType(**updated_webhook.model_dump())

    @strawberry.mutation
    async def delete_webhook(self, id: str) -> bool:
        """Delete a webhook subscription."""
        await webhook_service.delete_webhook(id)
        return True