from dotenv import load_dotenv
load_dotenv(
   dotenv_path = ".env" 
)

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

print("loaded env", os.environ["SUPABASE_URL"])


class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_SERVICE_ROLE_KEY: str
    STORAGE_ENGINE: str = "SUPABASE"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings(
    SUPABASE_URL = os.environ["SUPABASE_URL"],
    SUPABASE_KEY = os.environ["SUPABASE_KEY"],
    SUPABASE_JWT_SECRET = os.environ["SUPABASE_JWT_SECRET"],
    SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)
