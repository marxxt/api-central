import redis.asyncio as redis
import json
import redis.asyncio as redis
import json
from pydantic import BaseModel
from typing import List, Optional, Type, Any
import uuid # Import uuid for generating IDs if needed

class RedisAdapter: # Removed inheritance from AbstractStorageAdapter
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, ttl_seconds: int = 3600):
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = ttl_seconds

    def _get_key(self, model_type: Type[BaseModel], id: Any) -> str:
        """Generates a Redis key for a model instance."""
        return f"{model_type.__name__.lower()}:{id}"

    async def create(self, model_instance: BaseModel) -> BaseModel:
        """Creates a new record in Redis."""
        # Assuming the model instance might not have an ID yet, generate one
        # type: ignore comment to suppress Pylance error about missing 'id'
        if not hasattr(model_instance, 'id') or model_instance.id is None: # type: ignore
             # Generate a simple UUID for the ID
             model_instance.id = str(uuid.uuid4()) # type: ignore

        key = self._get_key(model_instance.__class__, model_instance.id) # type: ignore
        try:
            # Use setnx to ensure the key does not already exist (atomic create)
            success = await self.client.setnx(key, model_instance.model_dump_json())
            if not success:
                 # type: ignore comment to suppress Pylance error about missing 'id'
                 raise Exception(f"Record with id {model_instance.id} already exists in Redis.") # type: ignore
            # Set TTL after successful creation
            await self.client.expire(key, self.ttl)
            return model_instance
        except Exception as e:
            raise RuntimeError(f"[Redis] Failed to create record: {e}")

    async def read(self, model_type: Type[BaseModel], id: Any) -> Optional[BaseModel]:
        """Reads a record by ID from Redis."""
        key = self._get_key(model_type, id)
        raw_data = await self.client.get(key)

        if not raw_data:
            return None # Return None for cache miss

        try:
            data = json.loads(raw_data)
            # Ensure the 'id' from the key is in the data for model validation
            if 'id' not in data:
                 data['id'] = str(id)
            return model_type.model_validate(data)
        except Exception as e:
            raise ValueError(f"[Redis] Failed to parse cached data for {model_type.__name__} id {id}: {e}")

    async def update(self, model_instance: BaseModel) -> BaseModel:
        """Updates an existing record in Redis."""
        # Assuming the model instance has an 'id' attribute
        # type: ignore comment to suppress Pylance error about missing 'id'
        if not hasattr(model_instance, 'id') or model_instance.id is None: # type: ignore
             raise ValueError("Model instance must have an ID to update.")

        key = self._get_key(model_instance.__class__, model_instance.id) # type: ignore
        try:
            # Use set to update the existing key, maintaining the TTL
            await self.client.set(key, model_instance.model_dump_json(), ex=self.ttl)
            return model_instance
        except Exception as e:
            raise RuntimeError(f"[Redis] Failed to update record with id {model_instance.id}: {e}") # type: ignore


    async def delete(self, model_type: Type[BaseModel], id: Any) -> None:
        """Deletes a record by ID from Redis."""
        key = self._get_key(model_type, id)
        try:
            await self.client.delete(key)
        except Exception as e:
            raise RuntimeError(f"[Redis] Failed to delete record with id {id}: {e}")


    async def list(self, model_type: Type[BaseModel]) -> List[BaseModel]:
        """Lists all records of a given type from Redis."""
        # WARNING: Using KEYS can be blocking and should be avoided in production
        # on large datasets. Consider using SCAN or maintaining separate indices.
        pattern = f"{model_type.__name__.lower()}:*"
        keys = await self.client.keys(pattern)
        if not keys:
            return []

        raw_data_list = await self.client.mget(keys)
        items = []
        for raw_data, key in zip(raw_data_list, keys):
            if raw_data: # Ensure data exists for the key
                try:
                    data = json.loads(raw_data)
                    # Ensure the 'id' from the key is in the data for model validation
                    if 'id' not in data:
                         # Extract ID from key (e.g., "user:123" -> "123")
                         data['id'] = key.split(":", 1)[-1]
                    items.append(model_type.model_validate(data))
                except Exception as e:
                    print(f"[Redis] Failed to parse cached data for key {key}: {e}") # Log parsing errors
        return items
