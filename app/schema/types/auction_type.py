import strawberry
from models.auction import Seller, ReputationSummary, BidHistoryEntry, PropertyDetails

@strawberry.experimental.pydantic.type(model=Seller, all_fields=True)
class SellerType:
    pass

@strawberry.experimental.pydantic.type(model=ReputationSummary, all_fields=True)
class ReputationSummaryType:
    pass

@strawberry.experimental.pydantic.type(model=BidHistoryEntry, all_fields=True)
class BidHistoryEntryType:
    pass

@strawberry.experimental.pydantic.type(model=PropertyDetails, all_fields=True)
class PropertyDetailsType:
    pass

@strawberry.experimental.pydantic.input(model=Seller)
class SellerInput:
    # Fields that the client should provide when creating a seller
    name: str
    verified: bool
    # Exclude: id (if it were present on the model)