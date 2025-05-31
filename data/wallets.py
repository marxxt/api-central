import uuid
import random
from faker import Faker
from config import supabase_bot  # Reuse supabase_bot from your centralized config

fake = Faker()

def generate_fake_wallets(user_ids, num_wallets_per_user=2):
    """Generates fake wallet data."""
    wallets = []
    for user_id in user_ids:
        for _ in range(num_wallets_per_user):
            wallets.append({
                "user_id": user_id,
                "address": fake.sha256(),
                "balance": round(random.uniform(100, 100000), 2),
                "currency": random.choice(["USD", "ETH", "BTC", "USDC"])
            })
    return wallets

def insert_fake_wallets(wallets):
    """Inserts fake wallet data into Supabase via supabase_bot."""
    wallet_ids = []
    for wallet in wallets:
        try:
            response = supabase_bot.table("wallets").upsert(wallet).execute()
            print(f"✅ Inserted wallet for user {response.data[0]['id']}")
            wallet_ids.append(response.data[0]['id'])
        except Exception as e:
            print(f"❌ Exception while inserting wallet: {e}")
            
    return wallet_ids

if __name__ == "__main__":
    # Dummy test
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(3)]
    wallets_data = generate_fake_wallets(dummy_user_ids)
    insert_fake_wallets(wallets_data)
    print("🏁 Wallet data generation and insertion complete.")
