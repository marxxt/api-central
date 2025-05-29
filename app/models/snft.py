from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime

from strawberry import ID


# Enums
class TransactionCategory(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    TRANSFER = "TRANSFER"
    EXCHANGE = "EXCHANGE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"
    MINT = "MINT"


class AssetType(str, Enum):
    SFR = "SFR"
    MULTIFAMILY = "MULTIFAMILY"
    OFFICE = "OFFICE"
    STORAGE = "STORAGE"
    INDUSTRIAL = "INDUSTRIAL"
    RETAIL = "RETAIL"
    HOTEL = "HOTEL"
    LAND = "LAND"
    AGRICULTURAL = "AGRICULTURAL"
    MIXED_USE = "MIXED_USE"
    ART = "ART"
    COLLECTIBLE = "COLLECTIBLE"
    MEMBERSHIP = "MEMBERSHIP"
    EXPERIENCE = "EXPERIENCE"
    OTHER_NFT = "OTHER_NFT"


# Placeholder for transaction object
class Transaction(BaseModel):
    id: ID
    type: TransactionCategory
    amount: Optional[float] = None
    timestamp: Optional[datetime] = None


# SNFT model
class SNFT(BaseModel):
    id: ID
    wallet_id: ID
    name: str
    description: Optional[str] = None
    image_url: str
    price: float
    currency: Optional[str] = None  # ETH, USD, etc.
    created_at: datetime
    updated_at: Optional[datetime] = None
    # transactions: Optional[List[Transaction]] = None
    address: str
    creator: Optional[str] = None
    date_listed: Optional[datetime] = None
    status: Optional[str] = None
    category: Optional[str] = None  # AssetType | string
    collection_id: Optional[ID] = None
    collection_name: Optional[str] = None
    bid_price: Optional[str] = None
    numeric_bid_price: Optional[float] = None