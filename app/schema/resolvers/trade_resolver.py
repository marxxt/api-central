import strawberry
from schema.types.trade_type import PropertyListingType, PropertyListingInput, PropertyListingUpdateInput # Import input types

from services.trade_service import TradeService # Import the TradeService
from adapters import get_adapter # Import get_adapter
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from models.trade import PropertyListing # Import the model for validation
from strawberry.types import Info # Import Info
from app.main import event_publisher # Import the event_publisher instance

@strawberry.type
class Query:
    @strawberry.field
    # Access context via info argument
    async def listings(self, info: Info) -> list[PropertyListingType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        trade_service = TradeService(adapter, event_publisher) # Instantiate the service with event_publisher
        # Pass the authenticated_user_id to the service method
        listings = await trade_service.get_listings(authenticated_user_id) # Call the service method
        # Map the list of PropertyListing models to PropertyListingType
        # Manually map the list of PropertyListing models to PropertyListingType
        return [PropertyListingType(**listing.model_dump()) for listing in listings]

@strawberry.type
class Mutation:
    @strawberry.mutation
    # Access context via info argument
    async def create_listing(self, listing_data: PropertyListingInput, info: Info) -> PropertyListingType:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        trade_service = TradeService(adapter, event_publisher) # Instantiate the service with event_publisher

        # Convert input data to the Pydantic model
        # Note: Fields like id, user_id, created_at, etc. will be set by the service/adapter
        listing_model = PropertyListing.model_validate(listing_data.__dict__)
        listing_model.user_id = authenticated_user_id # Set user_id from authenticated user

        # Call the service method to create the listing
        created_listing = await trade_service.create_listing(authenticated_user_id, listing_model)

        # Return the created listing mapped to the GraphQL type
        # Manually map the created listing to the GraphQL type
        return PropertyListingType(**created_listing.model_dump())

    @strawberry.mutation
    # Access context via info argument
    async def update_listing(self, listing_data: PropertyListingUpdateInput, info: Info) -> PropertyListingType:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        trade_service = TradeService(adapter, event_publisher) # Instantiate the service with event_publisher

        # Convert input data to the Pydantic model
        # Assuming PropertyListingUpdateInput includes the ID for the listing to update
        listing_model = PropertyListing.model_validate(listing_data.__dict__)

        # Call the service method to update the listing
        updated_listing = await trade_service.update_listing(authenticated_user_id, listing_model)

        # Return the updated listing mapped to the GraphQL type
        # Manually map the updated listing to the GraphQL type
        return PropertyListingType(**updated_listing.model_dump())

    @strawberry.mutation
    # Access context via info argument
    async def delete_listing(self, id: strawberry.ID, info: Info) -> bool:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        trade_service = TradeService(adapter, event_publisher) # Instantiate the service with event_publisher

        # Call the service method to delete the listing
        await trade_service.delete_listing(authenticated_user_id, str(id))

        # Return True if deletion was successful (service method raises exception on failure)
        return True