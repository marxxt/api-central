from pydantic import BaseModel
from typing import Optional, List, Literal


# Enums / Literals
AuctionType = Literal["Whole Project", "Individual Tokens", "RRNFT", "Stay Reward"]
AuctionStatus = Literal["active", "completed", "pending", "cancelled"]
ParticipationStatus = Literal["low", "medium", "high", "trending low", "trending high"]
PropertyTypeDetail = Literal["Single Family", "Multi Family", "Condo", "Townhouse", "Commercial"]  # Extend as needed


# Reputation (embedded, stripped version)
class ReputationSummary(BaseModel):
    score: Optional[float] = None
    rank: Optional[str] = None
    ranking_percentile: Optional[str] = None
    last_updated: Optional[str] = None
    adjusted_staking_yield: Optional[str] = None
    forecast_access_level: Optional[str] = None


# Seller model
class Seller(BaseModel):
    name: str
    reputation: ReputationSummary
    verified: bool


# Bid history model
class BidHistoryEntry(BaseModel):
    id: str
    bidder: str
    amount: str
    time: str
    timestamp: int  # Unix ms


# Property Details
class PropertyDetails(BaseModel):
    size: str
    bedrooms: int
    bathrooms: float
    year_built: int
    amenities: List[str]
    participation_score: Optional[ParticipationStatus] = None
    occupancy_rate: Optional[str] = None
    lot_size: Optional[str] = None
    property_type_detail: Optional[PropertyTypeDetail] = None