import uuid
import random
from faker import Faker
from config import supabase_bot  # Use centralized Supabase client

fake = Faker()

def generate_fake_daos(property_ids):
    """Generates fake DAO data."""
    daos = []
    dao_types = ['single_property', 'multi_property', 'contractor', 'hedge_fund', 'realtor_team', 'reit', 'developer', 'community', 'guild', 'foundation', 'investor_club']
    scopes = ['local', 'regional', 'national', 'global']
    for property_id in range(property_ids):
        daos.append({
            "property_id": property_id,
            "name": fake.company() + " DAO",
            "link": fake.url(),
            "description": fake.paragraph(),
            "dao_type": random.choice(dao_types),
            "operational_scope": random.choice(scopes),
            "valuation": round(random.uniform(1_000_000, 100_000_000), 2),
            "currency": "USD",
            "total_token_supply": random.randint(1_000_000, 1_000_000_000),
            "treasury_address": fake.sha256(),
            "voting_token_address": fake.sha256(),
            "governance_model": random.choice(["1-token-1-vote", "quadratic", "liquid"])
        })
    return daos

def insert_fake_daos(daos):
    """Insert DAOs using Supabase upsert."""
    inserted_ids = []
    for dao in daos:
        try:
            response = supabase_bot.table("daos").upsert(dao).execute()
            inserted_id = response.data[0]['id']
            print(f"✅ Inserted DAO: {dao['name']} (ID: {inserted_id})")
            inserted_ids.append(inserted_id)
        except Exception as e:
            print(f"❌ Error inserting DAO {dao['name']}: {e}")
    return inserted_ids

if __name__ == "__main__":
    
    property_ids = [str(uuid.uuid4()) for _ in range(3)]
    daos_data = generate_fake_daos(property_ids)
    insert_fake_daos(daos_data)
    print("🏁 DAOs data generation and insertion complete.")
