from adapters.base import AbstractStorageAdapter
from adapters.caching_adapter import CachingAdapter # Import CachingAdapter
from adapters.redis_adapter import RedisAdapter # Import RedisAdapter
from models.auction import Seller # Import the Seller model
from typing import List, cast, Optional # Import List, cast, and Optional
from fastapi import HTTPException # Import HTTPException for authorization errors
from utils.logger import get_logger # Import get_logger

logger = get_logger(__name__) # Get logger instance

class SellerService:
    def __init__(self, adapter: AbstractStorageAdapter):
        self.adapter = adapter

    async def get_sellers(self) -> List[Seller]:
        """
        Retrieves a list of sellers using the configured adapter.
        """
        # Add any business logic related to fetching sellers here
        # Use the generic list method
        sellers = await self.adapter.list(Seller) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        return cast(List[Seller], sellers)

    async def get_seller_by_user_id(self, user_id: str) -> Optional[Seller]:
        """
        Retrieves a seller by their user ID, with caching if a CachingAdapter is used.
        Note: This implementation fetches all sellers and filters, which may not be efficient for large datasets.
        A more efficient approach would require adapter support for querying by specific fields.
        """
        # Construct a cache key based on model type and user ID
        cache_key = f"seller_user_id:{user_id}"
        logger.debug(f"Attempting to get seller for user {user_id} from cache with key: {cache_key}")

        cached_seller = None
        # Check if the adapter is a CachingAdapter to access the cache
        if isinstance(self.adapter, CachingAdapter):
            try:
                # Attempt to read from cache using the generic read method
                cached_seller = cast(Optional[Seller], await self.adapter.cache.read(Seller, user_id))
                if cached_seller:
                    logger.debug(f"Cache hit for seller with user ID: {user_id}")
                    return cached_seller

                logger.info(f"Cache miss for seller with user ID: {user_id}, hitting primary")
            except Exception as e:
                logger.error(f"Cache error while reading for seller with user ID {user_id}: {e}")
        else:
            logger.debug("Adapter is not a CachingAdapter, bypassing cache lookup in get_seller_by_user_id")


        # Cache miss or adapter is not CachingAdapter, fetch from primary (via list and filter)
        sellers = await self.adapter.list(Seller)
        found_seller = None
        for seller_item in sellers:
            # Cast the item to Seller to access user_id
            seller = cast(Seller, seller_item)
            # Assuming the Seller model now has a user_id field
            if hasattr(seller, 'user_id') and seller.user_id == user_id:
                found_seller = seller # Found the seller
                break # Exit loop once found

        # If seller was found and adapter is CachingAdapter, cache the result
        if found_seller and isinstance(self.adapter, CachingAdapter):
            try:
                logger.debug(f"Caching seller with user ID: {user_id}")
                # Use the generic create method to cache the seller object
                await self.adapter.cache.create(found_seller)
            except Exception as e:
                logger.error(f"Cache error while writing for seller with user ID {user_id}: {e}")

        return found_seller # Return the found seller or None

    async def create_seller(self, authenticated_user_id: str, seller_data: Seller) -> Seller:
        """
        Creates a new seller profile with authorization check.
        """
        # Authorization check: Example - only authenticated users can create seller profiles
        # This is a placeholder; replace with actual role/permission check if needed
        if not authenticated_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to create seller profiles")

        # Add any business logic related to creating a seller here
        # For example, link the seller profile to the authenticated_user_id
        # seller_data.user_id = authenticated_user_id # Assuming a user_id field exists on Seller model

        # Use the generic create method
        created_seller = await self.adapter.create(seller_data)
        # Explicitly cast the result to the expected type for the type checker
        return cast(Seller, created_seller)