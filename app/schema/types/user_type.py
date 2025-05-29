import strawberry
from models.user import User
import strawberry.federation as federation # Import strawberry.federation
from typing import Optional # Import Optional
from datetime import datetime # Import datetime for placeholder
from schema.types.reputation_type import ReputationType # Import ReputationType

@strawberry.experimental.pydantic.input(model=User, all_fields=True)
class UserInput:
    pass

@federation.type(keys=["id"]) # Use the federation.type decorator with keys
class UserType:
    id: strawberry.ID # Explicitly define the ID field for direct access

    # Add a placeholder resolve_reference class method
    @classmethod
    def resolve_reference(cls, id: strawberry.ID):
        # TODO: Implement logic to fetch a User by ID using the adapter
        # This method is called by the gateway to resolve entity references
        # For now, return a placeholder User instance with required fields
        from models.user import User # Import User model

        return User(
            id=id,
            user_id=id, # Assuming user_id is the same as id for simplicity in placeholder
            role="user", # Placeholder role
            created_at=datetime.now() # Placeholder creation time
            # Add other required fields from Profile if necessary with placeholder values
        )

    reputation: Optional[ReputationType] # Add the reputation field

    # Add Seller fields as extensions to UserType
    name: Optional[str] # Seller name
    verified: Optional[bool] # Seller verification status