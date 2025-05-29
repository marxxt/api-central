import phonenumbers
from pydantic import BaseModel, EmailStr
from typing import Annotated, Optional, List, Literal, Union
from datetime import datetime
from enum import Enum
from pydantic_extra_types.phone_numbers import PhoneNumberValidator

from strawberry import ID

PhoneNumberType = Annotated[ Union[str, phonenumbers.PhoneNumber], PhoneNumberValidator(supported_regions=['US'], default_region='US') ]

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
    id: ID
    amount: float


class SNFT(BaseModel):
    id: ID
    token_id: str


# Wallet Model
class Wallet(BaseModel):
    id: ID
    user_id: ID
    address: str
    balance: float
    currency: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    # transactions: Optional[List[Transaction]] = None
    nfts: Optional[List[SNFT]] = None


# Profile Model
class Profile(BaseModel):
    id: ID
    user_id: ID
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
    # wallets: Optional[List[Wallet]] = None


# Reputation Model
class Reputation(BaseModel):
    id: ID
    user_id: ID
    score: Optional[float] = None
    rank: Optional[Rank] = None
    ranking_percentile: Optional[str] = None
    last_updated: Optional[datetime] = None
    adjusted_staking_yield: Optional[str] = None
    forecast_access_level: Optional[str] = None


# Final User Model
class User(BaseModel):
    id: Optional[ID]
    display_name: str
    email: EmailStr
    phone: PhoneNumberType
    user_metadata: object
        
