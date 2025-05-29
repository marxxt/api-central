import strawberry
from typing import Optional # Import Optional
from schema.types.user_type import UserInput, UserType
from adapters import get_adapter
from models.user import User
from services.user_service import UserService # Import the new service
from services.reputation_service import ReputationService # Import ReputationService
from services.seller_service import SellerService # Import SellerService
from schema.types.reputation_type import ReputationType # Import ReputationType
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from strawberry.types import Info # Import Info

@strawberry.type
class Query:
    @strawberry.field
    # Access context via info argument
    async def user(self, id: strawberry.ID, info: Info) -> Optional[UserType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter()
        user_service = UserService(adapter) # Instantiate the service
        # Pass both authenticated_user_id and requested_user_id to the service method
        user = await user_service.get_user(authenticated_user_id, str(id)) # Call the service method
        if user is None:
            return None # Return None if user is not found (or not authorized, handled by service)
        # Manually map fields from Pydantic User to UserType
        return UserType(**user.model_dump())

@strawberry.type
class Mutation:
    @strawberry.mutation
    # Access context via info argument
    async def create_user(self, user_data: UserInput, info: Info) -> UserType:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state (might be None for public signup)
        authenticated_user_id = getattr(request.state, 'user_id', None)

        adapter = get_adapter()
        user_service = UserService(adapter) # Instantiate the service

        # Convert input data to the Pydantic model
        # Note: Fields like id, created_at, etc. will be set by the service/adapter
        user_model = User.model_validate(user_data.__dict__)

        # Call the service method to create the user
        created_user = await user_service.create_user(user_model)

        # Return the created user mapped to the GraphQL type
        # Manually map fields from Pydantic User to UserType
        return UserType(**created_user.model_dump())

    @strawberry.mutation
    # Access context via info argument
    async def update_user(self, user_data: UserInput, info: Info) -> UserType:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter()
        user_service = UserService(adapter) # Instantiate the service

        # Convert input data to the Pydantic model
        # Assuming UserInput includes the ID for the user to update
        user_model = User.model_validate(user_data.__dict__)

        # Call the service method to update the user
        updated_user = await user_service.update_user(authenticated_user_id, user_model)

        # Return the updated user mapped to the GraphQL type
        # Manually map fields from Pydantic User to UserType
        return UserType(**updated_user.model_dump())

    @strawberry.mutation
    # Access context via info argument
    async def delete_user(self, id: strawberry.ID, info: Info) -> bool:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter()
        user_service = UserService(adapter) # Instantiate the service

        # Call the service method to delete the user
        await user_service.delete_user(authenticated_user_id, str(id))

        # Return True if deletion was successful (service method raises exception on failure)
        return True

# Resolver for the 'reputation' field on UserType
@strawberry.field
async def resolve_reputation(self: UserType, info: Info) -> Optional[ReputationType]:
    request: Request = info.context["request"]
    # Access the user ID from the UserType instance (self)
    user_id = self.id

    # Get the adapter and instantiate the ReputationService
    adapter = get_adapter()
    reputation_service = ReputationService(adapter)

    # Fetch the user's reputation
    # Assuming get_user_reputation in ReputationService takes authenticated_user_id and target_user_id
    # For a field resolver, we might only need the target_user_id (self.id)
    # Let's assume get_user_reputation can work with just the target_user_id if auth is handled elsewhere
    # If authentication is needed here, we would use request.state.user_id
    # Pass the authenticated user ID and the target user ID to the service method
    authenticated_user_id = getattr(request.state, 'user_id', None) # Get authenticated user ID from request state
    if authenticated_user_id is None:
        raise HTTPException(status_code=403, detail="Authentication required to access reputation data")

    reputation = await reputation_service.get_user_reputation(authenticated_user_id, str(user_id))

    # Manually map the Pydantic Reputation model to ReputationType
    if reputation:
        # Assuming ReputationType can be instantiated directly from Pydantic model fields
        return ReputationType(**reputation.model_dump())
    return None

# Resolver for the 'name' field on UserType (Seller name)
@strawberry.field
async def resolve_name(self: UserType, info: Info) -> Optional[str]:
    request: Request = info.context["request"]
    user_id = self.id
    adapter = get_adapter()
    seller_service = SellerService(adapter)
    # Assuming get_seller_by_user_id exists and returns a Seller model
    seller = await seller_service.get_seller_by_user_id(str(user_id))
    return seller.name if seller else None

# Resolver for the 'verified' field on UserType (Seller verification status)
@strawberry.field
async def resolve_verified(self: UserType, info: Info) -> Optional[bool]:
    request: Request = info.context["request"]
    user_id = self.id
    adapter = get_adapter()
    seller_service = SellerService(adapter)
    # Assuming get_seller_by_user_id exists and returns a Seller model
    seller = await seller_service.get_seller_by_user_id(str(user_id))
    return seller.verified if seller else None