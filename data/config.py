# config.py

import os
from pydantic_settings import BaseSettings
from pydantic import AnyUrl, SecretStr
from typing import cast
from dotenv import load_dotenv

# Load environment variables from a .env file, if present
load_dotenv()

class Settings(BaseSettings):
    """
    Application configuration settings.
    Values are loaded from environment variables or a .env file.
    """

    # Supabase configurations
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_KEY: str

    # Application settings
    ENV: str = "development"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate the settings, so they can be imported elsewhere
settings = Settings(
    SUPABASE_URL = os.environ["SUPABASE_URL"],
    SUPABASE_KEY = os.environ["SUPABASE_KEY"],
    SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"],
)