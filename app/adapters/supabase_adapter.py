from supabase import create_client
from app.adapters.base import AbstractStorageAdapter
from app.models.user import UserModel
from app.config import settings

class SupabaseAdapter(AbstractStorageAdapter):
    def __init__(self):
        self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    async def get_user(self, id: str) -> UserModel:
        response = self.client.table("users").select("*").eq("id", id).execute()
        data = response.data
        if not data:
            raise ValueError("User not found")
        return UserModel.model_validate(data[0])

    async def store_user(self, user: UserModel) -> None:
        self.client.table("users").insert(user.model_dump()).execute()
