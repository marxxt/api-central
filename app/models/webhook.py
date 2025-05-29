from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class Webhook(BaseModel):
    """
    Represents a webhook subscription in the system.
    """
    id: str = Field(..., description="Unique identifier for the webhook")
    target_url: str = Field(..., description="The URL where the webhook payload will be sent")
    event_type: str = Field(..., description="The specific event that triggers this webhook (e.g., 'auction.created', 'trade.completed')")
    secret: str = Field(..., description="A shared secret for signing payloads, ensuring authenticity")
    owner_id: Optional[str] = Field(None, description="Optional: ID of the user or service that owns this webhook")
    is_active: bool = Field(True, description="Boolean flag to enable/disable the webhook")
    headers: Optional[Dict[str, Any]] = Field(None, description="Optional: JSON field for custom headers to be sent with the webhook")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the webhook was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of when the webhook was last updated")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat() + "Z"
        }
        populate_by_name = True
        arbitrary_types_allowed = True # Required for datetime