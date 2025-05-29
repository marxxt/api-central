import strawberry
from models.user import Profile

@strawberry.experimental.pydantic.type(model=Profile, all_fields=True)
class ProfileType:
    pass