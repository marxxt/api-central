import strawberry
from typing import Optional, List # Import Optional and List
from models.user import Wallet # Import Wallet model
import strawberry.federation as federation # Import strawberry.federation
from datetime import datetime # Import datetime for placeholder
from strawberry import ID # Import ID for type hinting
from schema.types.snft_type import SNFTType # Import SNFTType

@federation.type(keys=["id"]) # Use the federation.type decorator with keys
class WalletType:
    id: strawberry.ID
    user_id: strawberry.ID
    address: str
    balance: float
    currency: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    nfts: Optional[List[SNFTType]]

    # Add a placeholder resolve_reference class method
    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        # TODO: Implement logic to fetch a Wallet by ID
        # This method is called by the gateway to resolve entity references
        # For now, return a placeholder instance with required fields
        return Wallet(
            id=id,
            user_id=strawberry.ID("placeholder_user_id"), # Placeholder user_id, cast to strawberry.ID
            address="placeholder_address", # Placeholder address
            balance=0.0, # Placeholder balance
            created_at=datetime.now() # Placeholder created_at
            # Add other required fields from Wallet if necessary with placeholder values
        )