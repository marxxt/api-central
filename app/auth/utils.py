import jwt
from app.config import settings

def decode_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError as e:
        raise ValueError("Invalid JWT token") from e
