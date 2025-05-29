import strawberry
from models.property import PropertyMarketplaceItem, CollectionItem
from typing import Optional # Import Optional
from datetime import datetime # Import datetime
import strawberry.federation as federation # Import strawberry.federation

@federation.type(keys=["id"]) # Use the federation.type decorator with keys
class PropertyMarketplaceItemType:
    id: strawberry.ID
    user_id: str
    title: str
    location: str
    price: str
    numeric_price: float
    token_price: Optional[str]
    total_tokens: Optional[int]
    available_tokens: Optional[int]
    image: str
    type: Optional[str]
    roi: Optional[str]
    date_listed: datetime
    created_at: datetime
    updated_at: Optional[datetime]
    status: Optional[str]
    collection_name: Optional[str]
    collection_id: Optional[strawberry.ID]

    # Add a placeholder resolve_reference class method
    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        # TODO: Implement logic to fetch a PropertyMarketplaceItem by ID
        # This method is called by the gateway to resolve entity references
        # For now, return a placeholder instance with required fields
        return PropertyMarketplaceItem(
            id=id,
            user_id="placeholder_user_id", # Placeholder user_id
            title="Placeholder Property", # Placeholder title
            location="Placeholder Location", # Placeholder location
            price="0", # Placeholder price
            numeric_price=0.0, # Placeholder numeric_price
            image="placeholder.jpg", # Placeholder image
            date_listed=datetime.now(), # Placeholder date_listed
            created_at=datetime.now() # Placeholder created_at
            # Add other required fields from PropertyMarketplaceItem if necessary with placeholder values
        )

@strawberry.experimental.pydantic.type(model=CollectionItem, all_fields=True)
class CollectionItemType:
    pass

@strawberry.experimental.pydantic.input(model=PropertyMarketplaceItem)
class PropertyMarketplaceItemInput:
    # Fields that the client should provide when creating a marketplace item
    title: str
    location: str
    price: str
    numeric_price: float
    token_price: Optional[str]
    total_tokens: Optional[int]
    available_tokens: Optional[int]
    image: str
    type: Optional[str]
    roi: Optional[str]
    date_listed: datetime
    # Exclude: id, created_at, updated_at, status, collection_name, collection_id