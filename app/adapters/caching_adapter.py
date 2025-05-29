from adapters.base import AbstractStorageAdapter
from models.user import User
from utils.logger import get_logger
from typing import List, Optional, Type, Any # Import missing types
from pydantic import BaseModel # Import BaseModel
from typing import cast # Import cast

logger = get_logger(__name__)

class CachingAdapter(AbstractStorageAdapter):
    def __init__(
        self,
        cache: AbstractStorageAdapter,
        primary: AbstractStorageAdapter,
    ):
        self.cache = cache
        self.primary = primary

    async def create(self, model_instance: BaseModel) -> BaseModel:
        """Creates a new record in the primary adapter."""
        # Cache is not typically involved in creation in this pattern
        return await self.primary.create(model_instance)

    async def read(self, model_type: Type[BaseModel], id: Any) -> Optional[BaseModel]:
        """Reads a record, attempting cache first, then primary."""
        try:
            # Attempt to read from cache using the generic read method
            cached_result = await self.cache.read(model_type, id)
            if cached_result:
                logger.debug(f"[Cache] Cache hit for {model_type.__name__} with ID {id}")
                return cached_result
            logger.info(f"[Cache Miss] {model_type.__name__} with ID {id} not found in cache, hitting primary")
        except Exception as e:
            # Log cache read errors but don't fail the operation
            logger.error(f"[Cache Error] Error reading from cache for {model_type.__name__} with ID {id}: {e}")

        # Read from primary
        primary_result = await self.primary.read(model_type, id)

        # If found in primary, store in cache
        if primary_result:
            try:
                logger.debug(f"[Cache Fill] Storing {model_type.__name__} with ID {id} in cache")
                # Use the generic create or update method for caching
                # Assuming create is suitable for adding to cache
                await self.cache.create(primary_result)
            except Exception as e:
                logger.error(f"[Cache Error] Error writing to cache for {model_type.__name__} with ID {id}: {e}")

        return primary_result

    async def update(self, model_instance: BaseModel) -> BaseModel:
        """Updates a record in the primary adapter and invalidates cache."""
        # Update in primary
        updated_instance = await self.primary.update(model_instance)

        # Invalidate or update cache for the specific item
        try:
            # Assuming the model instance has an 'id' attribute
            item_id = getattr(updated_instance, 'id', None)
            if item_id:
                 # Attempt to delete from cache to invalidate using the generic delete method
                logger.debug(f"[Cache Invalidate] Invalidating cache for {updated_instance.__class__.__name__} with ID {item_id}")
                await self.cache.delete(updated_instance.__class__, item_id)
        except Exception as e:
             # Use getattr safely for item_id in error message as well
             error_item_id = getattr(updated_instance, 'id', 'N/A')
             logger.error(f"[Cache Error] Error invalidating cache for {updated_instance.__class__.__name__} with ID {error_item_id}: {e}")


        return updated_instance

    async def delete(self, model_type: Type[BaseModel], id: Any) -> None:
        """Deletes a record from the primary adapter and invalidates cache."""
        # Delete from primary
        await self.primary.delete(model_type, id)

        # Invalidate cache for the specific item
        try:
            logger.debug(f"[Cache Invalidate] Invalidating cache for {model_type.__name__} with ID {id}")
            await self.cache.delete(model_type, id)
        except Exception as e:
            logger.error(f"[Cache Error] Error invalidating cache for {model_type.__name__} with ID {id}: {e}")

    async def list(self, model_type: Type[BaseModel]) -> List[BaseModel]:
        """Lists all records from the primary adapter (caching list results is complex and often not done)."""
        # For simplicity, list operations typically bypass cache or use a separate caching strategy
        logger.debug(f"[Cache Bypass] Listing {model_type.__name__} from primary adapter")
        return await self.primary.list(model_type)
