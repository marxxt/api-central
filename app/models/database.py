from pydantic_extra_types.coordinate import Longitude, Latitude
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from strawberry import ID

class Location(BaseModel):
        longitude: Longitude
        latitude: Latitude

# Row returned from Supabase
class ProfileRow(BaseModel):
    id: str
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[Location] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Data to insert
class ProfileInsert(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[Location] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Data to update
class ProfileUpdate(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[Location] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None