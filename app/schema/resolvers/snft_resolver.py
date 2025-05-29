import strawberry
from schema.types.snft_type import SNFTType
from services.snft_service import SnftService # Import the SnftService
from adapters import get_adapter # Import get_adapter
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from strawberry.types import Info # Import Info

@strawberry.type
class Query:
    @strawberry.field
    # Access context via info argument
    async def snfts(self, info: Info) -> list[SNFTType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        snft_service = SnftService(adapter) # Instantiate the service
        # Pass the authenticated_user_id to the service method
        snfts = await snft_service.get_snfts(authenticated_user_id) # Call the service method
        # Map the list of SNFT models to SNFTType
        # Manually map the list of SNFT models to SNFTType
        return [SNFTType(**snft.model_dump()) for snft in snfts]