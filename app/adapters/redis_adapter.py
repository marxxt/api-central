import redis.asyncio as redis
import json
from app.adapters.base import AbstractStorageAdapter
from app.models.user import User


class RedisAdapter(AbstractStorageAdapter):
    def __init__(self, ttl_seconds: int = 3600):
        self.client = redis.from_url("redis://localhost:6379", decode_responses=True)
        self.ttl = ttl_seconds

    async def get_user(self, id: str) -> User:
        key = f"user:{id}"
        raw_data = await self.client.get(key)

        if not raw_data:
            raise KeyError(f"[Redis] Cache miss for user id: {id}")

        try:
            data = json.loads(raw_data)
            return User.model_validate(data)
        except Exception as e:
            raise ValueError(f"[Redis] Failed to parse cached user: {e}")

    async def store_user(self, user: User) -> None:
        key = f"user:{user.id}"
        try:
            await self.client.set(key, user.model_dump_json(), ex=self.ttl)
        except Exception as e:
            raise RuntimeError(f"[Redis] Failed to store user: {e}")
