import strawberry
from typing import Optional # Re-import Optional to ensure it's recognized
from models.snft import Transaction, TransactionCategory as TransactionModelType # Import Transaction and TransactionCategory enum
import strawberry.federation as federation # Import strawberry.federation
from datetime import datetime # Import datetime for placeholder

@federation.type(keys=["id"]) # Use the federation.type decorator with keys
class TransactionType:
    id: strawberry.ID
    type: TransactionModelType
    amount: Optional[float]
    timestamp: Optional[datetime]

    # Add a placeholder resolve_reference class method
    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        # TODO: Implement logic to fetch a Transaction by ID
        # This method is called by the gateway to resolve entity references
        # For now, return a placeholder instance with required fields
        return Transaction(
            id=id,
            type=TransactionModelType.UNKNOWN, # Placeholder type using the imported enum
            # Add other required fields from Transaction if necessary with placeholder values
        )