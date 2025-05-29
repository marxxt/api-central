from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime
from strawberry import ID

class PropertyMarketplaceItem(BaseModel):
    id: ID
    user_id: str # Add user_id field to link marketplace item to a user
    title: str
    location: str
    price: str
    numeric_price: float
    token_price: Optional[str] = None
    total_tokens: Optional[int] = None
    available_tokens: Optional[int] = None
    image: str
    type: Optional[str] = None
    roi: Optional[str] = None
    date_listed: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    status: Optional[str] = None
    collection_name: Optional[str] = None
    collection_id: Optional[ID] = None


class CollectionItem(BaseModel):
    id: ID
    user_id: str # Add user_id field to link collection to a user
    name: str
    color: str
    count: Optional[int] = None
