from adapters.base import AbstractStorageAdapter
from models.property import PropertyMarketplaceItem, CollectionItem
from typing import List, cast # Import cast
from fastapi import HTTPException # Import HTTPException for authorization errors

class PropertyService:
    def __init__(self, adapter: AbstractStorageAdapter):
        self.adapter = adapter

    async def get_marketplace_items(self, authenticated_user_id: str) -> List[PropertyMarketplaceItem]:
        """
        Retrieves a list of property marketplace items for the authenticated user using the configured adapter.
        """
        # Add any business logic related to fetching marketplace items here
        # Use the generic list method to get all marketplace items (or a filtered list if adapter supports it)
        all_marketplace_items = await self.adapter.list(PropertyMarketplaceItem) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        all_marketplace_items = cast(List[PropertyMarketplaceItem], all_marketplace_items)

        # Filter marketplace items to only include those belonging to the authenticated user
        user_marketplace_items = [
            item for item in all_marketplace_items
            if item.user_id == authenticated_user_id # Filter by user_id
        ]

        return user_marketplace_items

    async def get_collections(self, authenticated_user_id: str) -> List[CollectionItem]:
        """
        Retrieves a list of property collections for the authenticated user using the configured adapter.
        """
        # Add any business logic related to fetching collections here
        # Use the generic list method to get all collections (or a filtered list if adapter supports it)
        all_collections = await self.adapter.list(CollectionItem) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        all_collections = cast(List[CollectionItem], all_collections)

        # Filter collections to only include those belonging to the authenticated user
        user_collections = [
            collection for collection in all_collections
            if collection.user_id == authenticated_user_id # Filter by user_id
        ]

        return user_collections

    async def create_marketplace_item(self, authenticated_user_id: str, item_data: PropertyMarketplaceItem) -> PropertyMarketplaceItem:
        """
        Creates a new property marketplace item with authorization check.
        """
        # Authorization check: Example - only users with a specific role can create listings
        # This is a placeholder; replace with actual role/permission check
        # For now, we'll just check if the user is authenticated (user_id is not None)
        if not authenticated_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to create marketplace items")

        # Add any business logic related to creating a marketplace item here
        # For example, set the seller ID based on the authenticated_user_id
        # item_data.seller_id = authenticated_user_id # Assuming a seller_id field exists

        # Use the generic create method
        created_item = await self.adapter.create(item_data)
        # Explicitly cast the result to the expected type for the type checker
        return cast(PropertyMarketplaceItem, created_item)