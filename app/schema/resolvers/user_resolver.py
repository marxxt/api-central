import strawberry
from app.schema.types.user_type import UserInput, UserType
from app.adapters import get_adapter
from app.models.user import UserModel

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: str) -> UserType:
        adapter = get_adapter()
        user = await adapter.get_user(id)
        return UserType.from_pydantic(user)

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def store_user(self, user: UserInput) -> UserType:
        adapter = get_adapter()
        user_model = UserModel.model_validate(user.__dict__)
        await adapter.store_user(user_model)
        return UserType.from_pydantic(user_model)