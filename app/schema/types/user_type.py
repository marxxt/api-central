import strawberry
from app.models.user import UserModel

@strawberry.experimental.pydantic.input(model=UserModel, all_fields=True)
class UserInput:
    pass

@strawberry.experimental.pydantic.type(model=UserModel, all_fields=True)
class UserType:
    pass
