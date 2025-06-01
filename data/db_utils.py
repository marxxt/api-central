# data/db_utils.py

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from config import settings
# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY
SUPABASE_KEY = settings.SUPABASE_KEY

# Validate environment variables
if not SUPABASE_URL:
    raise ValueError("Missing SUPABASE_URL in environment variables.")
if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing SUPABASE_SERVICE_ROLE_KEY in environment variables.")
if not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_KEY in environment variables.")

# Initialize Supabase clients
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
supabase_bot: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
supabase_public: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
