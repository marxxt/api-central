from dotenv import load_dotenv
load_dotenv(
   dotenv_path = ".env" 
)

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# print("loaded env", os.environ["SUPABASE_URL"])


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_SERVICE_ROLE_KEY: str
    MONGODB_CONNECTION_STRING: str # Add MongoDB connection string
    MONGODB_DATABASE_NAME: str # Add MongoDB database name
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    STORAGE_ENGINE: str = "SUPABASE"
    DEBUG: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings(
    SUPABASE_URL = os.environ["SUPABASE_URL"],
    SUPABASE_KEY = os.environ["SUPABASE_KEY"],
    SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"],
    SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    MONGODB_CONNECTION_STRING = os.environ.get("MONGODB_CONNECTION_STRING", ""), # Get from env, provide default
    MONGODB_DATABASE_NAME = os.environ.get("MONGODB_DATABASE_NAME", ""), # Get from env, provide default
    REDIS_HOST = os.environ.get("REDIS_HOST", "localhost"), # Get from env, provide default
    REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379")), # Get from env, provide default, convert to int
    REDIS_DB = int(os.environ.get("REDIS_DB", "0")), # Get from env, provide default, convert to int
    DEBUG = os.environ.get("DEBUG", "True")
)
