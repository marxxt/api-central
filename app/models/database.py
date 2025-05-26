from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Row returned from Supabase
class ProfileRow(BaseModel):
    id: str
    user_id: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


# Data to insert
class ProfileInsert(BaseModel):
    id: Optional[str] = None
    user_id: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Data to update
class ProfileUpdate(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None