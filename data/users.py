import uuid
from faker import Faker
from supabase import Client
from config import supabase_admin  # <-- Reuse centralized config
import requests

fake = Faker()

def fetch_avatar(random: str):
    url = "https://i.pravatar.cc/150?u"+random
    return requests.get(url)

def generate_fake_users(num_users=10):
    """Generates fake user data for Supabase Auth."""
    users = []
    for _ in range(num_users):
        email = fake.unique.email()
        password = 'Password123'
        username = fake.unique.user_name()
        first_name = fake.first_name()
        last_name = fake.last_name()
        avatar_url = "https://i.pravatar.cc/150?u"+username
        users.append({
            "email": email,
            "password": password,
            "user_metadata": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": first_name+" "+last_name,
                "avatar_url": avatar_url
            }
        })
    return users

def insert_fake_users(supabase: Client, users):
    inserted_users = []
    for user in users:
        try:
            response = supabase.auth.admin.create_user({
                "email": user["email"],
                "password": user["password"],
                "user_metadata": user["user_metadata"],
                "email_confirm": True
            })
            
            # print(f"✅ Created: {response.user.id}")
            inserted_users.append(response.user.id)
        except Exception as e:
            print(f"❌ Error creating user {user['email']}: {e}")
    
    # print("user ids :", inserted_users, flush=True)
    return inserted_users

if __name__ == "__main__":
    fake_users = generate_fake_users(num_users=5)
    insert_fake_users(supabase_admin, fake_users)
