from adapters.base import AbstractStorageAdapter
from models.trade import PropertyListing
from typing import List, cast, Optional # Import Optional
from fastapi import HTTPException # Import HTTPException for authorization errors
from app.utils.event_publisher import EventPublisher # Import EventPublisher

class TradeService:
    def __init__(self, adapter: AbstractStorageAdapter, event_publisher: EventPublisher):
        self.adapter = adapter
        self.event_publisher = event_publisher

    async def get_listings(self, authenticated_user_id: str) -> List[PropertyListing]:
        """
        Retrieves a list of property listings for the authenticated user using the configured adapter.
        """
        # Add any business logic related to fetching listings here
        # Use the generic list method to get all listings (or a filtered list if adapter supports it)
        all_listings = await self.adapter.list(PropertyListing) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        all_listings = cast(List[PropertyListing], all_listings)

        # Filter listings to only include those belonging to the authenticated user
        user_listings = [
            listing for listing in all_listings
            if listing.user_id == authenticated_user_id # Filter by user_id
        ]

        return user_listings

    async def create_listing(self, authenticated_user_id: str, listing_data: PropertyListing) -> PropertyListing:
        """
        Creates a new property listing with authorization check.
        """
        # Authorization check: Ensure the authenticated user is creating a listing for themselves
        if listing_data.user_id != authenticated_user_id:
             raise HTTPException(status_code=403, detail="Not authorized to create listings for other users")

        # Add any business logic related to creating a listing here

        # Use the generic create method
        created_listing = await self.adapter.create(listing_data)
        # Explicitly cast the result to the expected type for the type checker
        created_listing = cast(PropertyListing, created_listing)
        
        # Publish trade.submitted event
        await self.event_publisher.publish(
            event_type="trade.submitted",
            payload=created_listing.model_dump(),
            is_realtime=True # Mark as real-time for WebSocket
        )
        return created_listing


    async def update_listing(self, authenticated_user_id: str, listing_data: PropertyListing) -> PropertyListing:
        """
        Updates an existing property listing with authorization check.
        """
        # Authorization check: Ensure the authenticated user is updating their own listing
        if listing_data.user_id != authenticated_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to update this listing")

        # Add any business logic related to updating a listing here

        # Use the generic update method
        updated_listing = await self.adapter.update(listing_data)
        # Explicitly cast the result to the expected type for the type checker
        updated_listing = cast(PropertyListing, updated_listing)

        # Check if price has changed and publish event
        # This requires fetching the old listing to compare, or passing old data
        # For simplicity, assuming listing_data contains the new state and we publish if it's an update
        # A more robust solution would compare old_listing.price with listing_data.price
        await self.event_publisher.publish(
            event_type="trade.price_changed",
            payload=updated_listing.model_dump(),
            is_realtime=True # Mark as real-time for WebSocket
        )
        return updated_listing

    async def delete_listing(self, authenticated_user_id: str, listing_id: str) -> None:
        """
        Deletes a property listing with authorization check.
        """
        # First, retrieve the listing to check ownership
        existing_listing = await self.adapter.read(PropertyListing, listing_id)
        if existing_listing is None:
            raise HTTPException(status_code=404, detail="Listing not found")

        # Ensure the retrieved object is a PropertyListing before accessing user_id
        if not isinstance(existing_listing, PropertyListing):
             raise RuntimeError("Unexpected data type from adapter read")

        # Authorization check: Ensure the authenticated user is deleting their own listing
        if existing_listing.user_id != authenticated_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this listing")

        # Add any business logic related to deleting a listing here

        # Use the generic delete method
        await self.adapter.delete(PropertyListing, listing_id)