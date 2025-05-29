import strawberry
from models.reputation import Reputation # Import Reputation from the correct model file

@strawberry.experimental.pydantic.type(model=Reputation, all_fields=True)
class ReputationType:
    pass