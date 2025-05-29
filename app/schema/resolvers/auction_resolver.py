import strawberry
from schema.types.auction_type import BidHistoryEntryType
from services.auction_service import AuctionService # Import the AuctionService
from adapters import get_adapter # Import get_adapter
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from strawberry.types import Info # Import Info

@strawberry.type
class Query:
    @strawberry.field
    # Access context via info argument
    async def bid_history(self, info: Info) -> list[BidHistoryEntryType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        auction_service = AuctionService(adapter) # Instantiate the service
        # Pass the authenticated_user_id to the service method
        bid_history_entries = await auction_service.get_bid_history(authenticated_user_id) # Call the service method
        # Map the list of BidHistoryEntry models to BidHistoryEntryType
        return [BidHistoryEntryType.from_pydantic(entry) for entry in bid_history_entries]