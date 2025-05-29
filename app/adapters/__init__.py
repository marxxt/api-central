from config import settings
from adapters.redis_adapter import RedisAdapter
from adapters.supabase_adapter import SupabaseAdapter
from adapters.firestore_adapter import FirestoreAdapter
from adapters.mongodb_adapter import MongoDBAdapter # Import MongoDBAdapter
from adapters.caching_adapter import CachingAdapter
from adapters.base import AbstractStorageAdapter

def get_adapter() -> AbstractStorageAdapter:
    redis = RedisAdapter(ttl_seconds=3600)

    if settings.STORAGE_ENGINE == "SUPABASE":
        return CachingAdapter(cache=redis, primary=SupabaseAdapter())
    elif settings.STORAGE_ENGINE == "FIRESTORE":
        return CachingAdapter(cache=redis, primary=FirestoreAdapter())
    elif settings.STORAGE_ENGINE == "MONGODB": # Add condition for MongoDB
        # Assuming settings has MONGODB_CONNECTION_STRING and MONGODB_DATABASE_NAME
        mongodb_adapter = MongoDBAdapter(
            connection_string=settings.MONGODB_CONNECTION_STRING,
            database_name=settings.MONGODB_DATABASE_NAME
        )
        return CachingAdapter(cache=redis, primary=mongodb_adapter)
    elif settings.STORAGE_ENGINE == "REDIS":
        return redis
    else:
        raise ValueError(f"Unsupported STORAGE_ENGINE: {settings.STORAGE_ENGINE}")
