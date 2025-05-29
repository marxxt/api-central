import pytest
import strawberry
from strawberry.federation import Schema # Import Schema from federation
from app.schema.resolvers import schema as federated_schema # Import the federated schema
from typing import Optional # Import Optional

# Helper function to execute GraphQL queries
async def execute_query(schema: Schema, query: str, variables: Optional[dict] = None):
    result = await schema.execute(query, variable_values=variables)
    return result.data, result.errors

# Test for schema introspection (basic check for federation capabilities)
@pytest.mark.asyncio
async def test_federated_schema_introspection():
    # This query checks for the presence of the _service and _entities fields
    # which are required for Federation
    query = """
        query {
            _service {
                sdl
            }
            _entities(representations: []) {
                __typename
            }
        }
    """
    data, errors = await execute_query(federated_schema, query)

    assert errors is None
    assert data is not None
    assert "_service" in data
    assert "_entities" in data
    assert "sdl" in data["_service"]

# Test for fetching a User entity by key
@pytest.mark.asyncio
async def test_fetch_user_entity():
    user_id = "test_user_id_123"
    query = """
        query($representations: [_Any!]!) {
            _entities(representations: $representations) {
                ... on User {
                    id
                    # Add other User fields you might want to test fetching
                    # email
                    # role
                }
            }
        }
    """
    variables = {
        "representations": [
            {
                "__typename": "User",
                "id": user_id
            }
        ]
    }
    data, errors = await execute_query(federated_schema, query, variables)

    assert errors is None
    assert data is not None
    assert "_entities" in data
    assert len(data["_entities"]) == 1
    user_entity = data["_entities"][0]
    assert user_entity is not None
    assert user_entity["__typename"] == "User"
    assert user_entity["id"] == user_id
    # Add assertions for other fetched fields if included in the query

# Test for fetching a PropertyMarketplaceItem entity by key
@pytest.mark.asyncio
async def test_fetch_property_entity():
    property_id = "test_property_id_456"
    query = """
        query($representations: [_Any!]!) {
            _entities(representations: $representations) {
                ... on PropertyMarketplaceItem {
                    id
                    # Add other PropertyMarketplaceItem fields
                    # title
                    # location
                }
            }
        }
    """
    variables = {
        "representations": [
            {
                "__typename": "PropertyMarketplaceItem",
                "id": property_id
            }
        ]
    }
    data, errors = await execute_query(federated_schema, query, variables)

    assert errors is None
    assert data is not None
    assert "_entities" in data
    assert len(data["_entities"]) == 1
    property_entity = data["_entities"][0]
    assert property_entity is not None
    assert property_entity["__typename"] == "PropertyMarketplaceItem"
    assert property_entity["id"] == property_id
    # Add assertions for other fetched fields

# Test for fetching a PropertyListing entity by key
@pytest.mark.asyncio
async def test_fetch_property_listing_entity():
    listing_id = "test_listing_id_789"
    query = """
        query($representations: [_Any!]!) {
            _entities(representations: $representations) {
                ... on PropertyListing {
                    id
                    # Add other PropertyListing fields
                    # name
                    # status
                }
            }
        }
    """
    variables = {
        "representations": [
            {
                "__typename": "PropertyListing",
                "id": listing_id
            }
        ]
    }
    data, errors = await execute_query(federated_schema, query, variables)

    assert errors is None
    assert data is not None
    assert "_entities" in data
    assert len(data["_entities"]) == 1
    listing_entity = data["_entities"][0]
    assert listing_entity is not None
    assert listing_entity["__typename"] == "PropertyListing"
    assert listing_entity["id"] == listing_id
    # Add assertions for other fetched fields

# Test for fetching an SNFT entity by key
@pytest.mark.asyncio
async def test_fetch_snft_entity():
    snft_id = "test_snft_id_abc"
    query = """
        query($representations: [_Any!]!) {
            _entities(representations: $representations) {
                ... on SNFT {
                    id
                    # Add other SNFT fields
                    # name
                    # price
                }
            }
        }
    """
    variables = {
        "representations": [
            {
                "__typename": "SNFT",
                "id": snft_id
            }
        ]
    }
    data, errors = await execute_query(federated_schema, query, variables)

    assert errors is None
    assert data is not None
    assert "_entities" in data
    assert len(data["_entities"]) == 1
    snft_entity = data["_entities"][0]
    assert snft_entity is not None
    assert snft_entity["__typename"] == "SNFT"
    assert snft_entity["id"] == snft_id
    # Add assertions for other fetched fields

# Test for fetching a Transaction entity by key
@pytest.mark.asyncio
async def test_fetch_transaction_entity():
    transaction_id = "test_transaction_id_def"
    query = """
        query($representations: [_Any!]!) {
            _entities(representations: $representations) {
                ... on Transaction {
                    id
                    # Add other Transaction fields
                    # type
                    # amount
                }
            }
        }
    """
    variables = {
        "representations": [
            {
                "__typename": "Transaction",
                "id": transaction_id
            }
        ]
    }
    data, errors = await execute_query(federated_schema, query, variables)

    assert errors is None
    assert data is not None
    assert "_entities" in data
    assert len(data["_entities"]) == 1
    transaction_entity = data["_entities"][0]
    assert transaction_entity is not None
    assert transaction_entity["__typename"] == "Transaction"
    assert transaction_entity["id"] == transaction_id
    # Add assertions for other fetched fields

# Test for fetching a Wallet entity by key
@pytest.mark.asyncio
async def test_fetch_wallet_entity():
    wallet_id = "test_wallet_id_ghi"
    query = """
        query($representations: [_Any!]!) {
            _entities(representations: $representations) {
                ... on Wallet {
                    id
                    # Add other Wallet fields
                    # address
                    # balance
                }
            }
        }
    """
    variables = {
        "representations": [
            {
                "__typename": "Wallet",
                "id": wallet_id
            }
        ]
    }
    data, errors = await execute_query(federated_schema, query, variables)

    assert errors is None
    assert data is not None
    assert "_entities" in data
    assert len(data["_entities"]) == 1
    wallet_entity = data["_entities"][0]
    assert wallet_entity is not None
    assert wallet_entity["__typename"] == "Wallet"
    assert wallet_entity["id"] == wallet_id
    # Add assertions for other fetched fields

# Test for a query that fetches User and their Reputation and Seller info
@pytest.mark.asyncio
async def test_user_with_reputation_and_seller_info():
    user_id = "test_user_id_456" # Use a different ID or ensure resolve_reference can handle it
    query = """
        query {
            user(id: "%s") {
                id
                # Fields from User model
                # email
                # role
                # Fields from Reputation (resolved by field resolver)
                reputation {
                    score
                    rank
                }
                # Fields from Seller (resolved by field resolvers)
                name
                verified
            }
        }
    """ % user_id
    # Note: This test assumes the user resolver and the reputation/seller field resolvers
    # are correctly implemented to fetch data based on the user ID.
    # The placeholder resolve_reference methods in type files will return dummy data,
    # so this test might need to be adjusted or mocked for a real scenario.

    data, errors = await execute_query(federated_schema, query)

    assert errors is None
    assert data is not None
    assert "user" in data
    user_data = data["user"]
    assert user_data is not None
    assert user_data["id"] == user_id
    # Assertions for reputation and seller fields would go here
    # assert "reputation" in user_data
    # assert "name" in user_data
    # assert "verified" in user_data
    # assert user_data["reputation"]["score"] is not None # Example assertion
    # assert user_data["name"] is not None # Example assertion
    # assert user_data["verified"] is not None # Example assertion