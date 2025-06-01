from faker import Faker
from supabase import Client
from db_utils import supabase_admin
from pydantic import BaseModel, EmailStr, Field
from typing import List

fake = Faker()

class UserMetadata(BaseModel):
    username: str
    first_name: str
    last_name: str
    full_name: str
    avatar_url: str

class UserInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    user_metadata: UserMetadata

def fetch_avatar(unique_string: str) -> str:
    return f"https://i.pravatar.cc/150?u={unique_string}"

def generate_fake_users(num_users: int = 10) -> List[UserInput]:
    users = []
    for _ in range(num_users):
        email = fake.unique.email()
        username = fake.unique.user_name()
        first_name = fake.first_name()
        last_name = fake.last_name()
        full_name = f"{first_name} {last_name}"
        avatar_url = fetch_avatar(username)
        
        user_metadata = UserMetadata(
            username=username,
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            avatar_url=avatar_url
        )
        
        user = UserInput(
            email=email,
            password="Password123",
            user_metadata=user_metadata
        )
        users.append(user)
    return users

def insert_fake_users(supabase: Client, users: List[UserInput]) -> List[str]:
    inserted_users = []
    for user in users:
        try:
            response = supabase.auth.admin.create_user({
                "email": user.email,
                "password": user.password,
                "user_metadata": user.user_metadata.model_dump()
            })
            inserted_users.append(response.user.id)
        except Exception as e:
            print(f"❌ Error creating user {user.email}: {e}")
    return inserted_users

if __name__ == "__main__":
    fake_users = generate_fake_users(num_users=5)
    insert_fake_users(supabase_admin, fake_users)
