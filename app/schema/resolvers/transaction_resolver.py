import strawberry
from typing import List # Import List
from schema.types.transaction_type import TransactionType
from services.transaction_service import TransactionService # Import the TransactionService
from adapters import get_adapter # Import get_adapter
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from strawberry.types import Info # Import Info

@strawberry.type
class Query:
    @strawberry.field
    # Access context via info argument
    async def user_transactions(self, id: strawberry.ID, info: Info) -> List[TransactionType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        transaction_service = TransactionService(adapter) # Instantiate the service
        # Pass both authenticated_user_id and requested_user_id to the service method
        user_transactions = await transaction_service.get_user_transactions(authenticated_user_id, str(id)) # Call the service method
        # Map the list of Transaction models to TransactionType
        # Manually map the list of Transaction models to TransactionType
        return [TransactionType(**transaction.model_dump()) for transaction in user_transactions]