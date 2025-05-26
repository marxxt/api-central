from app.config import settings
from app.adapters.redis_adapter import RedisAdapter
from app.adapters.supabase_adapter import SupabaseAdapter
from app.adapters.firestore_adapter import FirestoreAdapter
from app.adapters.caching_adapter import CachingAdapter
from app.adapters.base import AbstractStorageAdapter

def get_adapter() -> AbstractStorageAdapter:
    redis = RedisAdapter(ttl_seconds=3600)

    if settings.STORAGE_ENGINE == "SUPABASE":
        return CachingAdapter(cache=redis, primary=SupabaseAdapter())
    elif settings.STORAGE_ENGINE == "FIRESTORE":
        return CachingAdapter(cache=redis, primary=FirestoreAdapter())
    elif settings.STORAGE_ENGINE == "REDIS":
        return redis
    else:
        raise ValueError(f"Unsupported STORAGE_ENGINE: {settings.STORAGE_ENGINE}")
