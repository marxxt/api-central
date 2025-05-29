import pytest
from app.schema.resolvers import schema
from app.models.user import User

@pytest.mark.asyncio
async def test_store_user_mutation(monkeypatch):
    class MockAdapter:
        async def store_user(self, user: User):
            return None

    monkeypatch.setattr("adapters.get_adapter", lambda: MockAdapter())

    query = """
    mutation {
        storeUser(user: {
            id: "abc123",
            full_name: "Mock User",
            email: "mock@example.com"
        }) {
            id
            fullName
            email
        }
    }
    """

    result = await schema.execute(query)

    # Add diagnostics for debugging
    if result.errors:
        for error in result.errors:
            print("GraphQL Error:", error.message)

    assert result.errors is None
    assert result.data is not None
    assert result.data["storeUser"]["id"] == "abc123"
