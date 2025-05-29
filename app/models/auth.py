from pydantic import BaseModel
from typing import Optional, Union, List

class TokenPayload(BaseModel):
    sub: str  # user ID
    email: Optional[str]
    role: Union[str, List[str]] = "user"  # Supabase may send role as string or list
    exp: Optional[int]
