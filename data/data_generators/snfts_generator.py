import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
from config import supabase_bot  # 🔁 Reuse shared client

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
                "bid_price": str(round(random.uniform(500, 90000), 2)),
                "metadata_status": random.choice(['complete', 'pending', 'failed']),
                "numeric_bid_price": round(random.uniform(500, 90000), 2),
                "status": random.choice(statuses),
                "property_id": prop_id,
                "contract_address": fake.sha256(),
                "dao_id": dao_id,
                "trust_id": str(uuid.uuid4()) if random.random() > 0.5 else None,
                "total_tokens": random.randint(10000, 1000000),
                "tokens_sold": random.randint(0, 50000),
                "token_price": round(random.uniform(0.1, 10.0), 2),
                "sale_status": random.choice(sale_statuses),
                "metadata_uri": fake.url(),
                "metadata_hash": fake.sha256(),
                "legal_doc_urls": {"trust_agreement": fake.url(), "dao_agreement": fake.url()} if random.random() > 0.5 else None,
                "notarization_status": random.choice(['pending', 'complete', 'rejected']),
                "wizard_progress": {"step": random.randint(1, 5), "completed": random.sample(['property', 'images', 'docs', 'mint'], k=random.randint(0, 4))},
                "deployed_at": fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc).isoformat() if random.random() > 0.3 else None,
                "preview_uri": fake.url() if random.random() > 0.2 else None,
                "expires_at": fake.date_time_between(start_date="now", end_date="+6m", tzinfo=timezone.utc).isoformat()
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
