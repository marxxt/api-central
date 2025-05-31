import os
from dotenv import load_dotenv
from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("SUPABASE_URL :", SUPABASE_URL)

if not SUPABASE_URL:
    raise ValueError("Missing SUPABASE_URL in .env")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing SUPABASE_SERVICE_ROLE_KEY in .env")

if not SUPABASE_KEY:
    raise ValueError("Missing SUPABASE_KEY in .env")

# 🔐 Admin client (auth.admin access)
supabase_admin: Client = create_client(
    SUPABASE_URL, 
    SUPABASE_SERVICE_ROLE_KEY,
    options=SyncClientOptions(
        auto_refresh_token=False,
        persist_session=False,
    )
)

# 🤖 Bot/Service client (for server-to-server interaction)
supabase_bot: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# 👤 User client (for frontend or authenticated sessions)
supabase_public: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
