import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from db_utils import supabase_bot  # 🔁 Reuse shared client

fake = Faker()

def generate_fake_snfts(wallet_ids, owner_ids, collection_ids, property_ids, dao_ids, num_snfts_per_property=1):
    """Generates fake SNFT data."""
    snfts = []
    statuses = ['draft', 'property_added', 'docs_uploaded', 'pending_signature', 'notarized', 'metadata_ready', 'minted']
    sale_statuses = ['open', 'closed', 'paused']

    for prop_id in property_ids:
        for _ in range(num_snfts_per_property):
            wallet_id = random.choice(wallet_ids) if wallet_ids else None
            owner_id = random.choice(owner_ids) if owner_ids else None
            collection_id = random.choice(collection_ids) if collection_ids else None
            dao_id = random.choice(dao_ids) if dao_ids else None

            snfts.append({
                "wallet_id": wallet_id,
                "owner_id": owner_id,
                "dao_id": dao_id,
                "name": fake.word().capitalize() + " SNFT",
                "description": fake.paragraph(),
                "image_url": fake.image_url(),
                "price": round(random.uniform(1000, 100000), 2),
                "currency": random.choice(["USD", "ETH", "USDC"]),
                "address": fake.address(),
                "creator": fake.name(),
                "date_listed": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc).isoformat(),
                "category": fake.word(),
                "collection_id": collection_id,
                "metadata_status": random.choice(['complete', 'pending', 'failed']),
                "status": random.choice(statuses),
            })
    return snfts

def insert_fake_snfts(snfts):
    """Inserts SNFTs into Supabase."""
    snft_ids = []
    for snft in snfts:
        try:
            response = supabase_bot.table("snfts").upsert(snft).execute()
            inserted_id = response.data[0]["id"]
            print(f"✅ Inserted SNFT: {snft['name']} -> {inserted_id}")
            snft_ids.append(inserted_id)
        except Exception as e:
            print(f"❌ Error inserting SNFT {snft['name']}: {e}")
    return snft_ids

if __name__ == "__main__":
    dummy_wallet_ids = [str(uuid.uuid4()) for _ in range(3)]
    dummy_owner_ids = [str(uuid.uuid4()) for _ in range(3)]
    dummy_collection_ids = [str(uuid.uuid4()) for _ in range(3)]
    dummy_property_ids = [str(uuid.uuid4()) for _ in range(3)]
    dummy_dao_ids = [str(uuid.uuid4()) for _ in range(3)]

    snfts_data = generate_fake_snfts(dummy_wallet_ids, dummy_owner_ids, dummy_collection_ids, dummy_property_ids, dummy_dao_ids)
    insert_fake_snfts(snfts_data)
    print("🏁 SNFTs generation and insertion complete.")
