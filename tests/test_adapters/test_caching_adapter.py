import pytest
from app.adapters.caching_adapter import CachingAdapter
from app.adapters.base import AbstractStorageAdapter
from app.models.user import User
from datetime import datetime

@pytest.mark.asyncio
async def test_get_user_hits_cache():
    class MockCache(AbstractStorageAdapter):
        async def get_user(self, id: str) -> User:
            return User(id=id, user_id=id, first_name="Cached", last_name="User", email="cached@example.com", role="USER", created_at=datetime.utcnow())

        async def store_user(self, user: User) -> None:
            pass

    class MockPrimary(AbstractStorageAdapter):
        async def get_user(self, id: str) -> User:
            raise RuntimeError("Should not be called")

        async def store_user(self, user: User) -> None:
            pass

    adapter = CachingAdapter(cache=MockCache(), primary=MockPrimary())
    user = await adapter.get_user("abc123")
    assert user.first_name == "Cached"

@pytest.mark.asyncio
async def test_get_user_falls_back_to_primary():
    class MockCache(AbstractStorageAdapter):
        async def get_user(self, id: str) -> User:
            raise KeyError("Cache miss")

        async def store_user(self, user: User) -> None:
            assert user.id == "abc123"

    class MockPrimary(AbstractStorageAdapter):
        async def get_user(self, id: str) -> User:
            return User(id=id, user_id=id, first_name="Primary", last_name="User", email="primary@example.com", role="USER", created_at=datetime.utcnow())

        async def store_user(self, user: User) -> None:
            pass

    adapter = CachingAdapter(cache=MockCache(), primary=MockPrimary())
    user = await adapter.get_user("abc123")
    assert user.first_name == "Primary"

@pytest.mark.asyncio
async def test_store_user_stores_in_both():
    events = []

    class MockCache(AbstractStorageAdapter):
        async def store_user(self, user: User) -> None:
            events.append("cache")

        async def get_user(self, id: str) -> User:
            return User(id=id, user_id=id, first_name="Ignored", last_name="User", email="n/a", role="USER", created_at=datetime.utcnow())

    class MockPrimary(AbstractStorageAdapter):
        async def store_user(self, user: User) -> None:
            events.append("primary")

        async def get_user(self, id: str) -> User:
            return User(id=id, user_id=id, first_name="Ignored", last_name="User", email="n/a", role="USER", created_at=datetime.utcnow())

    adapter = CachingAdapter(cache=MockCache(), primary=MockPrimary())
    await adapter.store_user(User(id="abc123", user_id="abc123", first_name="Log", last_name="Test", email="log@example.com", role="USER", created_at=datetime.utcnow()))
    assert "primary" in events and "cache" in events

@pytest.mark.asyncio
async def test_cache_and_primary_both_fail():
    class BrokenCache(AbstractStorageAdapter):
        async def get_user(self, id: str) -> User:
            raise KeyError("Cache failure")

        async def store_user(self, user: User) -> None:
            raise RuntimeError("Cannot store in cache")

    class BrokenPrimary(AbstractStorageAdapter):
        async def get_user(self, id: str) -> User:
            raise RuntimeError("Primary DB failure")

        async def store_user(self, user: User) -> None:
            raise RuntimeError("Primary store failed")

    adapter = CachingAdapter(cache=BrokenCache(), primary=BrokenPrimary())
    with pytest.raises(RuntimeError, match="Primary DB failure"):
        await adapter.get_user("abc123")

@pytest.mark.asyncio
async def test_primary_store_fails_but_cache_succeeds():
    events = []

    class MockCache(AbstractStorageAdapter):
        async def store_user(self, user: User) -> None:
            events.append("cache")

        async def get_user(self, id: str) -> User:
            return User(id=id, user_id=id, first_name="Backup", last_name="Cache", email="b@example.com", role="USER", created_at=datetime.utcnow())

    class FailingPrimary(AbstractStorageAdapter):
        async def store_user(self, user: User) -> None:
            raise RuntimeError("Primary write error")

        async def get_user(self, id: str) -> User:
            return User(id=id, user_id=id, first_name="Backup", last_name="Primary", email="b@example.com", role="USER", created_at=datetime.utcnow())

    adapter = CachingAdapter(cache=MockCache(), primary=FailingPrimary())
    with pytest.raises(RuntimeError, match="Primary write error"):
        await adapter.store_user(User(id="abc123", user_id="abc123", first_name="Bad", last_name="Write", email="bad@example.com", role="USER", created_at=datetime.utcnow()))

    assert "cache" not in events  # We assume primary failure stops dual write