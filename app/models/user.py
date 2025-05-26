from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


# Enums
class Rank(str, Enum):
    SSS = "SSS"
    SS = "SS"
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


# Placeholder for imported Transaction and SNFT
class Transaction(BaseModel):
    id: str
    amount: float


class SNFT(BaseModel):
    id: str
    token_id: str


# Wallet Model
class Wallet(BaseModel):
    id: str
    user_id: str
    address: str
    balance: float
    currency: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    transactions: Optional[List[Transaction]] = None
    nfts: Optional[List[SNFT]] = None


# Profile Model
class Profile(BaseModel):
    id: str
    user_id: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str  # from UserRole enum (should be referenced if declared elsewhere)
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    wallets: Optional[List[Wallet]] = None


# Reputation Model
class Reputation(BaseModel):
    id: str
    user_id: str
    score: Optional[float] = None
    rank: Optional[Rank] = None
    ranking_percentile: Optional[str] = None
    last_updated: Optional[datetime] = None
    adjusted_staking_yield: Optional[str] = None
    forecast_access_level: Optional[str] = None


# Final User Model
class User(Profile):
    reputation: Optional[Reputation] = None