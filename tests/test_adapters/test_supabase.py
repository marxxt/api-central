import pytest
from unittest.mock import AsyncMock
from app.adapters.supabase_adapter import SupabaseAdapter
from app.models.user import UserModel

@pytest.mark.asyncio
async def test_get_user_returns_valid_user(monkeypatch):
    adapter = SupabaseAdapter()

    mock_response = {"data": [{"id": "abc123", "full_name": "Jane Doe", "email": "jane@example.com"}]}
    mock_client = AsyncMock()
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response

    monkeypatch.setattr(adapter, "client", mock_client)

    user = await adapter.get_user("abc123")
    assert isinstance(user, UserModel)
    assert user.full_name == "Jane Doe"
