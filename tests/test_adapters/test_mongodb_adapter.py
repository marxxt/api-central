from bson.objectid import ObjectId # Import ObjectId
import pytest
from app.adapters.mongodb_adapter import MongoDBAdapter
from pydantic import BaseModel
from typing import Optional, List, Type, Any
from unittest.mock import AsyncMock, patch

# Define a simple Pydantic model for testing
class TestModel(BaseModel):
    id: Optional[str] = None
    name: str
    value: int

# Mock MongoDB client and database for testing
@pytest.fixture
def mock_mongo_client():
    with patch('motor.motor_asyncio.AsyncIOMotorClient') as MockClient:
        mock_client_instance = MockClient.return_value
        mock_db = AsyncMock()
        mock_client_instance.__getitem__.return_value = mock_db
        yield mock_db

@pytest.fixture
def mongodb_adapter(mock_mongo_client):
    # Use a dummy connection string and db name for the adapter
    adapter = MongoDBAdapter(connection_string="mongodb://test:27017/", database_name="testdb")
    # Replace the real db with the mock db
    adapter.db = mock_mongo_client
    return adapter

# Basic test for create method
@pytest.mark.asyncio
async def test_create(mongodb_adapter):
    test_instance = TestModel(name="Test Item", value=123)

    # Mock the insert_one method
    mock_insert_one_result = AsyncMock()
    mock_insert_one_result.inserted_id = "test_id" # Simulate MongoDB ObjectId
    mongodb_adapter.db["testmodel"].insert_one = AsyncMock(return_value=mock_insert_one_result)

    created_instance = await mongodb_adapter.create(test_instance)

    mongodb_adapter.db["testmodel"].insert_one.assert_called_once()
    assert created_instance.id == "test_id"
    assert created_instance.name == "Test Item"
    assert created_instance.value == 123

# Test for read method
@pytest.mark.asyncio
async def test_read(mongodb_adapter):
    test_id = "test_id"
    test_document = {"_id": ObjectId(test_id), "name": "Test Item", "value": 123}

    # Mock find_one to return a document
    mongodb_adapter.db["testmodel"].find_one = AsyncMock(return_value=test_document)

    read_instance = await mongodb_adapter.read(TestModel, test_id)

    mongodb_adapter.db["testmodel"].find_one.assert_called_once_with({"_id": ObjectId(test_id)})
    assert isinstance(read_instance, TestModel)
    assert read_instance.id == test_id
    assert read_instance.name == "Test Item"
    assert read_instance.value == 123

# Test for read method when document not found
@pytest.mark.asyncio
async def test_read_not_found(mongodb_adapter):
    test_id = "non_existent_id"

    # Mock find_one to return None
    mongodb_adapter.db["testmodel"].find_one = AsyncMock(return_value=None)

    read_instance = await mongodb_adapter.read(TestModel, test_id)

    mongodb_adapter.db["testmodel"].find_one.assert_called_once_with({"_id": ObjectId(test_id)})
    assert read_instance is None

# Test for update method
@pytest.mark.asyncio
async def test_update(mongodb_adapter):
    test_id = "test_id"
    updated_instance = TestModel(id=test_id, name="Updated Item", value=456)

    # Mock replace_one to indicate a successful update
    mock_update_result = AsyncMock()
    mock_update_result.matched_count = 1
    mongodb_adapter.db["testmodel"].replace_one = AsyncMock(return_value=mock_update_result)

    result = await mongodb_adapter.update(updated_instance)

    mongodb_adapter.db["testmodel"].replace_one.assert_called_once_with(
        {"_id": ObjectId(test_id)},
        updated_instance.model_dump(by_alias=True, exclude_unset=True, exclude={'id'})
    )
    assert isinstance(result, TestModel)
    assert result.id == test_id
    assert result.name == "Updated Item"
    assert result.value == 456

# Test for update method when document not found
@pytest.mark.asyncio
async def test_update_not_found(mongodb_adapter):
    test_id = "non_existent_id"
    updated_instance = TestModel(id=test_id, name="Updated Item", value=456)

    # Mock replace_one to indicate no document was matched
    mock_update_result = AsyncMock()
    mock_update_result.matched_count = 0
    mongodb_adapter.db["testmodel"].replace_one = AsyncMock(return_value=mock_update_result)

    with pytest.raises(ValueError, match=f"Document with ID {test_id} not found for update"):
        await mongodb_adapter.update(updated_instance)

    mongodb_adapter.db["testmodel"].replace_one.assert_called_once_with(
        {"_id": ObjectId(test_id)},
        updated_instance.model_dump(by_alias=True, exclude_unset=True, exclude={'id'})
    )

# Test for delete method
@pytest.mark.asyncio
async def test_delete(mongodb_adapter):
    test_id = "test_id"

    # Mock delete_one to indicate a successful deletion
    mock_delete_result = AsyncMock()
    mock_delete_result.deleted_count = 1
    mongodb_adapter.db["testmodel"].delete_one = AsyncMock(return_value=mock_delete_result)

    await mongodb_adapter.delete(TestModel, test_id)

    mongodb_adapter.db["testmodel"].delete_one.assert_called_once_with({"_id": ObjectId(test_id)})

# Test for delete method when document not found
@pytest.mark.asyncio
async def test_delete_not_found(mongodb_adapter):
    test_id = "non_existent_id"

    # Mock delete_one to indicate no document was deleted
    mock_delete_result = AsyncMock()
    mock_delete_result.deleted_count = 0
    mongodb_adapter.db["testmodel"].delete_one = AsyncMock(return_value=mock_delete_result)

    with pytest.raises(ValueError, match=f"Document with ID {test_id} not found for deletion"):
        await mongodb_adapter.delete(TestModel, test_id)

    mongodb_adapter.db["testmodel"].delete_one.assert_called_once_with({"_id": ObjectId(test_id)})

# Test for list method
@pytest.mark.asyncio
async def test_list(mongodb_adapter):
    test_documents = [
        {"_id": ObjectId("id1"), "name": "Item 1", "value": 1},
        {"_id": ObjectId("id2"), "name": "Item 2", "value": 2},
    ]

    # Mock find to return an async iterator
    mock_cursor = AsyncMock()
    mock_cursor.__aiter__.return_value = test_documents
    mongodb_adapter.db["testmodel"].find = AsyncMock(return_value=mock_cursor)

    listed_instances = await mongodb_adapter.list(TestModel)

    mongodb_adapter.db["testmodel"].find.assert_called_once_with({})
    assert isinstance(listed_instances, list)
    assert len(listed_instances) == 2
    assert all(isinstance(item, TestModel) for item in listed_instances)
    assert listed_instances[0].id == "id1"
    assert listed_instances[1].name == "Item 2"

# Test for list method when collection is empty
@pytest.mark.asyncio
async def test_list_empty(mongodb_adapter):
    # Mock find to return an empty async iterator
    mock_cursor = AsyncMock()
    mock_cursor.__aiter__.return_value = []
    mongodb_adapter.db["testmodel"].find = AsyncMock(return_value=mock_cursor)

    listed_instances = await mongodb_adapter.list(TestModel)

    mongodb_adapter.db["testmodel"].find.assert_called_once_with({})
    assert isinstance(listed_instances, list)
    assert len(listed_instances) == 0