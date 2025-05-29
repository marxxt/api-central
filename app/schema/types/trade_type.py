import strawberry
from models.trade import PriceHistoryEntry, PropertyListing, OrderFormState, CandlestickDataPoint, VolumeDataPoint
from typing import Optional # Import Optional
from datetime import datetime # Import datetime
import strawberry.federation as federation # Import strawberry.federation

@strawberry.experimental.pydantic.type(model=PriceHistoryEntry, all_fields=True)
class PriceHistoryEntryType:
    pass

@federation.type(keys=["id"]) # Use the federation.type decorator with keys
class PropertyListingType:
    id: strawberry.ID
    user_id: str
    name: str
    address: str
    image_url: str
    token_symbol: str
    current_price: float
    price_unit: str
    apy: Optional[float]
    valuation: float
    tokens_offered: Optional[int]
    total_tokens: Optional[int]
    is_favorite: Optional[bool]
    status: str
    price_history: Optional[list[PriceHistoryEntryType]]

    # Add a placeholder resolve_reference class method
    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        # TODO: Implement logic to fetch a PropertyListing by ID
        # This method is called by the gateway to resolve entity references
        # For now, return a placeholder instance with required fields
        return PropertyListing(
            id=id,
            user_id="placeholder_user_id", # Placeholder user_id
            name="Placeholder Listing", # Placeholder name
            address="Placeholder Address", # Placeholder address
            image_url="placeholder.jpg", # Placeholder image_url
            token_symbol="PLCH", # Placeholder token_symbol
            current_price=0.0, # Placeholder current_price
            price_unit="USD", # Placeholder price_unit
            valuation=0.0, # Placeholder valuation
            status="For Sale" # Placeholder status
            # Add other required fields from PropertyListing if necessary with placeholder values
        )


@strawberry.experimental.pydantic.input(model=OrderFormState, all_fields=True)
class OrderFormStateInput:
    pass

@strawberry.experimental.pydantic.input(model=PropertyListing)
class PropertyListingInput:
    # Fields for creating a listing
    name: str
    address: str
    image_url: str
    token_symbol: str
    current_price: float
    price_unit: str
    apy: Optional[float]
    valuation: float
    tokens_offered: Optional[int]
    total_tokens: Optional[int]
    is_favorite: Optional[bool]
    status: str
    date_listed: datetime
    # Exclude: id, user_id, created_at, updated_at, price_history, ohlc_history, volume_history

@strawberry.experimental.pydantic.input(model=PropertyListing)
class PropertyListingUpdateInput:
    # Fields for updating a listing
    id: strawberry.ID # Include ID for updates
    name: Optional[str] = None
    address: Optional[str] = None
    image_url: Optional[str] = None
    token_symbol: Optional[str] = None
    current_price: Optional[float] = None
    price_unit: Optional[str] = None
    apy: Optional[float] = None
    valuation: Optional[float] = None
    tokens_offered: Optional[int] = None
    total_tokens: Optional[int] = None
    is_favorite: Optional[bool] = None
    status: Optional[str] = None
    date_listed: Optional[datetime] = None
    # Exclude: user_id, created_at, updated_at, price_history, ohlc_history, volume_history


@strawberry.experimental.pydantic.type(model=VolumeDataPoint)
class VolumeDataPointType:
    time: datetime
    value: float
    color: Optional[str]