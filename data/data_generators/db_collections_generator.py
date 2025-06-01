import random
from typing import Annotated, List
import uuid
from pydantic import BaseModel, Field, conint
from faker import Faker
from db_utils import supabase_bot  # Use the shared Supabase client
PositiveInt = Annotated[conint(gt=0), Field(description="int value greater than 0")]

fake = Faker()

# 🎨 Pydantic schema
class Collection(BaseModel):
    user_id: str
    name: str
    color: str = Field(..., pattern=r"^#[A-Fa-f0-9]{6}$")
    count: PositiveInt

def generate_fake_collections(user_ids: List[str], num_collections_per_user: int = 1) -> List[Collection]:
    """Generates fake collection data."""
    collections = []
    for user_id in user_ids:
        for _ in range(num_collections_per_user):
            collections.append(Collection(
                user_id=user_id,
                name=fake.word().capitalize() + " Collection",
                color=fake.hex_color(),
                count=random.randint(1, 50)
            ))
    return collections

def insert_fake_collections(collections: List[Collection]) -> List[str]:
    """Inserts fake collection data into Supabase."""
    collection_ids = []
    for collection in collections:
        try:
            response = supabase_bot.table("collections").upsert(collection.model_dump()).execute()
            inserted = response.data[0]
            print(f"✅ Inserted collection: {inserted['name']} with id: {inserted['id']}")
            collection_ids.append(inserted["id"])
        except Exception as e:
            print(f"❌ Error inserting collection {collection.name}: {e}")
    return collection_ids

if __name__ == "__main__":
    dummy_user_ids = [str(uuid.uuid4() for _ in range(3))]
    collections_data = generate_fake_collections(dummy_user_ids)
    insert_fake_collections(collections_data)
    print("🏁 Collections data generation and insertion complete.")
