import strawberry
from schema.types.auction_type import SellerType, SellerInput # Import SellerInput
from services.seller_service import SellerService # Import the SellerService
from adapters import get_adapter # Import get_adapter
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from models.auction import Seller # Import the Seller model for validation
from strawberry.types import Info # Import Info

@strawberry.type
class Query:
    @strawberry.field
    async def sellers(self) -> list[SellerType]:
        adapter = get_adapter() # Get the adapter
        seller_service = SellerService(adapter) # Instantiate the service
        sellers = await seller_service.get_sellers() # Call the service method
        # Map the list of Seller models to SellerType
        return [SellerType.from_pydantic(seller) for seller in sellers]

@strawberry.type
class Mutation:
    @strawberry.mutation
    # Access context via info argument
    async def create_seller(self, seller_data: SellerInput, info: Info) -> SellerType:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        seller_service = SellerService(adapter) # Instantiate the service

        # Convert input data to the Pydantic model
        seller_model = Seller.model_validate(seller_data.__dict__)

        # Call the service method to create the seller
        created_seller = await seller_service.create_seller(authenticated_user_id, seller_model)

        # Return the created seller mapped to the GraphQL type
        return SellerType.from_pydantic(created_seller)