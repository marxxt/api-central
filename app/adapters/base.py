from abc import ABC, abstractmethod
from app.models.user import UserModel

class AbstractStorageAdapter(ABC):
    @abstractmethod
    async def get_user(self, id: str) -> UserModel:
        pass

    @abstractmethod
    async def store_user(self, user: UserModel) -> None:
        pass
