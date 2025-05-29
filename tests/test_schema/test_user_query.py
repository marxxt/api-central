import pytest
from schema.resolvers import schema
from adapters import get_adapter
from models.user import User
from schema.types.user_type import UserType


@pytest.mark.asyncio
async def test_user_query(monkeypatch):
    # Mock adapter to replace get_user call
    class MockAdapter:
        async def get_user(self, id) -> User:
            return User(id=id, full_name="Mock User", email="mock@example.com")

    monkeypatch.setattr("adapters.get_adapter", lambda: MockAdapter())

    query = """
    query {
        user(id: "abc123") {
            id
            fullName
            email
        }
    }
    """

    result = await schema.execute(query)
    assert result.errors is None
    assert result.data is not None
    assert result.data["user"]["id"] == "abc123"
    assert result.data["user"]["fullName"] == "Mock User"
