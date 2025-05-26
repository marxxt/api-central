import pytest
from app.adapters.redis_adapter import RedisAdapter
from app.models.user import UserModel
import json

@pytest.mark.asyncio
async def test_redis_get_user(monkeypatch):
    adapter = RedisAdapter()

    class MockRedis:
        async def get(self, key):
            return json.dumps({"id": "abc123", "full_name": "Jane Redis", "email": "redis@example.com"})
        async def set(self, key, value):
            return "OK"

    monkeypatch.setattr(adapter, "client", MockRedis())
    user = await adapter.get_user("abc123")
    assert user.email == "redis@example.com"