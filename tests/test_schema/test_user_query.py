import pytest
from app.schema.resolvers import schema
from app.adapters import get_adapter
from app.models.user import UserModel
from app.schema.types.user_type import UserType


@pytest.mark.asyncio
async def test_user_query(monkeypatch):
    # Mock adapter to replace get_user call
    class MockAdapter:
        async def get_user(self, id: str) -> UserModel:
            return UserModel(id=id, full_name="Mock User", email="mock@example.com")

    monkeypatch.setattr("app.adapters.get_adapter", lambda: MockAdapter())

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
