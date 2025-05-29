from adapters.base import AbstractStorageAdapter
from models.auction import BidHistoryEntry
from typing import List, cast # Import cast
from fastapi import HTTPException # Import HTTPException for authorization errors

class AuctionService:
    def __init__(self, adapter: AbstractStorageAdapter):
        self.adapter = adapter

    async def get_bid_history(self, authenticated_user_id: str) -> List[BidHistoryEntry]:
        """
        Retrieves a list of bid history entries for the authenticated user using the configured adapter.
        """
        # Add any business logic related to fetching bid history here
        # Use the generic list method to get all bid history entries (or a filtered list if adapter supports it)
        all_bid_history = await self.adapter.list(BidHistoryEntry) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        all_bid_history = cast(List[BidHistoryEntry], all_bid_history)

        # Filter bid history entries to only include those belonging to the authenticated user
        user_bid_history = [
            entry for entry in all_bid_history
            if entry.bidder == authenticated_user_id # Assuming bidder field matches user ID
        ]

        return user_bid_history