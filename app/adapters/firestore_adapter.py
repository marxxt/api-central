from google.cloud.firestore_v1 import AsyncClient
from app.adapters.base import AbstractStorageAdapter
from app.models.user import UserModel

class FirestoreAdapter(AbstractStorageAdapter):
    def __init__(self):
        self.client = AsyncClient()

    async def get_user(self, id: str) -> UserModel:
        doc_ref = self.client.collection("users").document(id)
        doc = await doc_ref.get()
        if not doc.exists:
            raise ValueError("User not found")
        return UserModel.model_validate(doc.to_dict())

    async def store_user(self, user: UserModel) -> None:
        doc_ref = self.client.collection("users").document(user.id)
        await doc_ref.set(user.model_dump())
