import strawberry
from typing import Optional # Import Optional
from schema.types.reputation_type import ReputationType
from services.reputation_service import ReputationService # Import the ReputationService
from adapters import get_adapter # Import get_adapter
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from strawberry.types import Info # Import Info

@strawberry.type
class Query:
    @strawberry.field
    async def reputations(self) -> list[ReputationType]:
        adapter = get_adapter() # Get the adapter
        reputation_service = ReputationService(adapter) # Instantiate the service
        reputations = await reputation_service.get_reputations() # Call the service method
        # Map the list of Reputation models to ReputationType
        return [ReputationType.from_pydantic(reputation) for reputation in reputations]

    @strawberry.field
    # Access context via info argument
    async def user_reputation(self, id: strawberry.ID, info: Info) -> Optional[ReputationType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        reputation_service = ReputationService(adapter) # Instantiate the service
        # Pass both authenticated_user_id and requested_user_id to the service method
        reputation = await reputation_service.get_user_reputation(authenticated_user_id, str(id)) # Call the service method
        if reputation is None:
            return None # Return None if reputation is not found (or not authorized, handled by service)
        return ReputationType.from_pydantic(reputation)