# data_seeding/user_seeder.py
from typing import List, Dict, Any
from faker import Faker
from gotrue import SyncGoTrueAdminAPI, UserResponse
from gotrue.types import AdminUserAttributes # Import AdminUserAttributes

# Import the generator function
from .fake_data_generators import generate_user_payload

def seed_users(
    count: int,
    admin_auth_client: SyncGoTrueAdminAPI,
    fake: Faker
) -> List[str]:
    """
    Creates multiple users in Supabase Auth using the admin client.

    Args:
        count: The number of users to create.
        admin_auth_client: The initialized Supabase Auth Admin client.
        fake: The Faker instance.

    Returns:
        A list of IDs of the successfully created users.
    """
    user_ids: List[str] = []
    # Track emails/phones locally to improve uniqueness attempts within this run
    existing_emails: set = set()
    existing_phones: set = set()

    print(f"--- Creating {count} Users ---")

    for i in range(count):
        try:
            # Generate the user payload using the generator function
            user_payload = generate_user_payload(fake, existing_emails, existing_phones)
            # print(user_payload)
            if not user_payload.get("email") and not user_payload.get("phone"):
                 print(f"⚠️ Skipping user {i+1}: Generator failed to produce email or phone.")
                 continue # Skip if payload is invalid
            
            # Use the admin_auth_client to create the user
            # Arguments mirror generate_user_payload keys
            create_args: Dict[str, Any] = {
                 "email": user_payload.get("email"),
                 "phone": user_payload.get("phone"),
                 "user_metadata": user_payload.get("user_metadata", {}),
            }
            
            # Remove None values from args
            create_args = {k: v for k, v in create_args.items() if v is not None}
            
            # Create an instance of AdminUserAttributes
            attributes_obj = AdminUserAttributes(**create_args)
            result: UserResponse  = admin_auth_client.create_user(attributes=attributes_obj)

            if result and result.user:
                user_id = result.user.id
                user_ids.append(user_id)
                print(f"✅ User {i+1} created: ID={user_id}, Email={user_payload.get('email')}, Phone={user_payload.get('phone')}")
            else:
                 print(f"⚠️ User creation succeeded but returned no user data for user {i+1}.")


        except Exception as e:
            print(f"❌ Exception during user creation API call for user {i+1}: {e}")

    return user_ids