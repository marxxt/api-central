import strawberry
from models.database import ProfileRow, ProfileInsert, ProfileUpdate

@strawberry.experimental.pydantic.type(model=ProfileRow, all_fields=True)
class ProfileRowType:
    pass

@strawberry.experimental.pydantic.input(model=ProfileInsert, all_fields=True)
class ProfileInsertInput:
    pass

@strawberry.experimental.pydantic.input(model=ProfileUpdate, all_fields=True)
class ProfileUpdateInput:
    pass