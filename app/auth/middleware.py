from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from config import settings
from models.auth import TokenPayload
from typing import List, Optional, Union

PUBLIC_ROUTES = ["/", "/graphql", "/health"]
ALLOWED_ROLES = ["admin", "broker", "user"]  # Modify as needed

def is_public_request(request: Request, body: Optional[bytes] = None) -> bool:
    if request.method == "GET" and request.url.path in PUBLIC_ROUTES:
        return True
    if request.method == "POST" and request.url.path == "/graphql":
        if body and (b"introspection" in body or b"__schema" in body):
            return True
    return False

def decode_jwt_token(token: str) -> TokenPayload:
    try:
        decoded = jwt.decode(token, settings.SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return TokenPayload.model_validate(decoded)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token processing error: {str(e)}")

def has_valid_role(role: Union[str, List[str]]) -> bool:
    if isinstance(role, str):
        return role in ALLOWED_ROLES
    return any(r in ALLOWED_ROLES for r in role)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.DEBUG:
            return await call_next(request)

        body = None
        if request.method == "POST" and request.url.path == "/graphql":
            body = await request.body()

        if is_public_request(request, body):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        token = auth_header.split(" ")[1]
        payload = decode_jwt_token(token)

        if not has_valid_role(payload.role):
            raise HTTPException(status_code=403, detail="Insufficient role permissions")

        request.state.user_id = payload.sub
        request.state.role = payload.role

        return await call_next(request)

# Use inside protected resolvers
# from fastapi import Request

# def some_protected_resolver(info):
#     request: Request = info.context["request"]
#     if request.state.role != "admin":
#         raise HTTPException(status_code=403, detail="Only admins can access this.")
