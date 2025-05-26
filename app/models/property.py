from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime


class PropertyMarketplaceItem(BaseModel):
    id: Union[int, str]
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
    collection_id: Optional[str] = None


class CollectionItem(BaseModel):
    id: str
    name: str
    color: str
    count: Optional[int] = None
