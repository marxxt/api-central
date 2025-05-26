from app.adapters.base import AbstractStorageAdapter
from app.models.user import UserModel
from app.utils.logger import get_logger

logger = get_logger(__name__)

class CachingAdapter(AbstractStorageAdapter):
    def __init__(
        self,
        cache: AbstractStorageAdapter,
        primary: AbstractStorageAdapter,
    ):
        self.cache = cache
        self.primary = primary

    async def get_user(self, id: str) -> UserModel:
        try:
            logger.debug(f"[Cache] Attempting to get user {id} from cache")
            return await self.cache.get_user(id)
        except KeyError:
            logger.info(f"[Cache Miss] User {id} not found in cache, hitting primary")
            user = await self.primary.get_user(id)
            logger.debug(f"[Cache Fill] Storing user {id} in cache")
            await self.cache.store_user(user)
            return user

    async def store_user(self, user: UserModel) -> None:
        logger.debug(f"[Store] Writing user {user.id} to primary and cache")
