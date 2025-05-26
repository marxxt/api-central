from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.auth.utils import decode_jwt

class SupabaseAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        try:
            user_data = decode_jwt(token)
            request.state.user = user_data
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token") from e

        response = await call_next(request)
        return response
