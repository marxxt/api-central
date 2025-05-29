# data_seeding/supabase_client.py
import os
from dotenv import load_dotenv
from supabase.client import create_client, Client # Import Client type for hinting
from supabase.lib.client_options import SyncClientOptions # Correct options type

# Load environment variables from .env file
load_dotenv()

# --- Supabase Configuration ---
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the environment or .env file")

# --- Client Initialization ---
# Use SyncClientOptions specifically for the synchronous client
options = SyncClientOptions(
    auto_refresh_token=False,
    persist_session=False,
)

# Initialize the standard Supabase client (used for RLS-enabled table operations)
# For seeding with service role key, you often use the SERVICE_ROLE_KEY here too
# However, the admin client is separate for auth operations.
# For table inserts in seeding, the SERVICE_ROLE_KEY bypasses RLS, which is usually desired.
# Let's initialize the main client with the service role key for seeding insertions.
# Note: Be cautious with this client instance elsewhere if RLS is critical.
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
    options
)

# Initialize the Supabase Auth Admin client (special use case for admin auth operations)
# This client is automatically available via the main client when using the service role key.
admin_auth_client = supabase.auth.admin

# --- Exports ---
__all__ = ["supabase", "admin_auth_client"]