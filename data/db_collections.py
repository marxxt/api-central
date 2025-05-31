import uuid
import random
from faker import Faker
from config import supabase_bot  # Use the shared Supabase client

fake = Faker()

def generate_fake_collections(user_ids, num_collections_per_user=1):
    """Generates fake collection data."""
    collections = []
    for user_id in user_ids:
        for _ in range(num_collections_per_user):
            collections.append({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": fake.word().capitalize() + " Collection",
                "color": fake.hex_color(),
                "count": random.randint(1, 50)
            })
    return collections

def insert_fake_collections(collections):
    """Inserts fake collection data into Supabase."""
    collection_ids = []
    for collection in collections:
        try:
            response = supabase_bot.table("collections").upsert(collection).execute()
            inserted = response.data[0]
            print(f"✅ Inserted collection: {inserted['name']} with id: {inserted['id']}")
            collection_ids.append(inserted["id"])
        except Exception as e:
            print(f"❌ Error inserting collection {collection['name']}: {e}")
    return collection_ids

if __name__ == "__main__":
    # Dummy test
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(3)]
    collections_data = generate_fake_collections(dummy_user_ids)
    insert_fake_collections(collections_data)
    print("🏁 Collections data generation and insertion complete.")
