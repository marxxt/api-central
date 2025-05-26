from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime


# Enums
class TransactionType(str, Enum):
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
    id: str
    type: TransactionType
    amount: Optional[float] = None
    timestamp: Optional[datetime] = None


# SNFT model
class SNFT(BaseModel):
    id: str
    wallet_id: str
    name: str
    description: Optional[str] = None
    image_url: str
    price: float
    currency: Optional[str] = None  # ETH, USD, etc.
    created_at: datetime
    updated_at: Optional[datetime] = None
    transactions: Optional[List[Transaction]] = None
    address: str
    creator: Optional[str] = None
    date_listed: Optional[datetime] = None
    status: Optional[str] = None
    category: Optional[str] = None  # AssetType | string
    collection_id: Optional[str] = None
    collection_name: Optional[str] = None
    bid_price: Optional[str] = None
    numeric_bid_price: Optional[float] = None