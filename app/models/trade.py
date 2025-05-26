from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime


# Core Data Points
class CandlestickDataPoint(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    value: Optional[float] = None
    color: Optional[str] = None


class VolumeDataPoint(BaseModel):
    time: datetime
    value: float
    color: Optional[str] = None


# Price Units
PriceUnit = Literal["USDC", "ETH", "USD"]
ListingStatus = Literal["For Sale", "Auction", "Rented", "Sold"]
OrderType = Literal["buy", "sell", "bid"]


# Property Listing
class PropertyListing(BaseModel):
    id: str
    name: str
    address: str
    image_url: str
    token_symbol: str
    current_price: float
    price_unit: PriceUnit
    apy: Optional[float] = None
    valuation: float
    tokens_offered: Optional[int] = None
    total_tokens: Optional[int] = None
    is_favorite: Optional[bool] = None
    status: ListingStatus
    price_history: Optional[List[dict]] = None  # [{'date': str, 'price': float}]
    ohlc_history: Optional[List[CandlestickDataPoint]] = None
    volume_history: Optional[List[VolumeDataPoint]] = None


# Order Form State
class OrderFormState(BaseModel):
    order_type: OrderType
    amount: str
    price_per_token: Optional[str] = None
    slippage: Optional[str] = None
    duration: Optional[str] = None