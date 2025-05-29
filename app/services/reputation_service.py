from adapters.base import AbstractStorageAdapter
from models.reputation import Reputation
from typing import List, cast, Optional # Import List, cast, and Optional
from fastapi import HTTPException # Import HTTPException for authorization errors

class ReputationService:
    def __init__(self, adapter: AbstractStorageAdapter):
        self.adapter = adapter

    async def get_reputations(self) -> List[Reputation]:
        """
        Retrieves a list of reputation entries using the configured adapter.
        (Note: This method might be less useful with user-specific reputation)
        """
        # Add any business logic related to fetching reputations here
        # Use the generic list method
        reputations = await self.adapter.list(Reputation) # Call the adapter method with the model type
        # Explicitly cast the result to the expected type for the type checker
        return cast(List[Reputation], reputations)

    async def get_user_reputation(self, authenticated_user_id: str, requested_user_id: str) -> Optional[Reputation]:
        """
        Retrieves a specific user's reputation with authorization check.
        """
        # Authorization check: Ensure the authenticated user is requesting their own reputation
        if authenticated_user_id != requested_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user's reputation data")

        # Add any business logic related to fetching a user's reputation here
        # Use the generic read method
        reputation = await self.adapter.read(Reputation, requested_user_id)
        # The read method returns BaseModel or None, ensure it's a Reputation if not None
        return reputation if isinstance(reputation, Reputation) else None