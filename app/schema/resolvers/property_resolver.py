import strawberry
from schema.types.property_type import PropertyMarketplaceItemType, CollectionItemType, PropertyMarketplaceItemInput # Import PropertyMarketplaceItemInput
from services.property_service import PropertyService # Import the PropertyService
from adapters import get_adapter # Import get_adapter
from fastapi import Request, HTTPException # Import Request and HTTPException from fastapi
from models.property import PropertyMarketplaceItem # Import the model for validation
from strawberry.types import Info # Import Info

@strawberry.type
class Query:
    @strawberry.field
    # Access context via info argument
    async def marketplace_items(self, info: Info) -> list[PropertyMarketplaceItemType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        property_service = PropertyService(adapter) # Instantiate the service
        # Pass the authenticated_user_id to the service method
        marketplace_items = await property_service.get_marketplace_items(authenticated_user_id) # Call the service method
        # Map the list of PropertyMarketplaceItem models to PropertyMarketplaceItemType
        # Manually map the list of PropertyMarketplaceItem models to PropertyMarketplaceItemType
        return [PropertyMarketplaceItemType(**item.model_dump()) for item in marketplace_items]

    @strawberry.field
    # Access context via info argument
    async def collections(self, info: Info) -> list[CollectionItemType]:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        property_service = PropertyService(adapter) # Instantiate the service
        # Pass the authenticated_user_id to the service method
        collections = await property_service.get_collections(authenticated_user_id) # Call the service method
        # Map the list of CollectionItem models to CollectionItemType
        # Manually map the list of CollectionItem models to CollectionItemType
        return [CollectionItemType(**collection.model_dump()) for collection in collections]

@strawberry.type
class Mutation:
    @strawberry.mutation
    # Access context via info argument
    async def create_marketplace_item(self, item_data: PropertyMarketplaceItemInput, info: Info) -> PropertyMarketplaceItemType:
        request: Request = info.context["request"]
        # Extract authenticated user ID from request state
        authenticated_user_id = request.state.user_id

        adapter = get_adapter() # Get the adapter
        property_service = PropertyService(adapter) # Instantiate the service

        # Convert input data to the Pydantic model
        # Note: Fields like id, created_at, etc. will be set by the service/adapter
        item_model = PropertyMarketplaceItem.model_validate(item_data.__dict__)

        # Call the service method to create the item
        created_item = await property_service.create_marketplace_item(authenticated_user_id, item_model)

        # Return the created item mapped to the GraphQL type
        # Manually map the created item to the GraphQL type
        return PropertyMarketplaceItemType(**created_item.model_dump())