import pytest
from app.adapters.firestore_adapter import FirestoreAdapter
from app.models.user import UserModel

@pytest.mark.asyncio
async def test_firestore_adapter(monkeypatch):
    adapter = FirestoreAdapter()

    class MockDoc:
        def __init__(self, exists=True):
            self.exists = exists

        def to_dict(self):
            return {"id": "abc123", "full_name": "Jane Fire", "email": "fire@example.com"}

    class MockRef:
        async def get(self):
            return MockDoc()

        async def set(self, _):
            return None

    class MockClient:
        def collection(self, _):
            return self
        def document(self, _):
            return MockRef()

    monkeypatch.setattr(adapter, "client", MockClient())
    user = await adapter.get_user("abc123")
    assert user.id == "abc123"