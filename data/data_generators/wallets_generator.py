import uuid
import random
from decimal import Decimal
from faker import Faker
from typing import List, Annotated
from pydantic import BaseModel, Field
from pydantic.types import condecimal

PositiveDecimal = Annotated[condecimal(gt=0), Field(description="Decimal value greater than 0")]
from db_utils import supabase_bot

fake = Faker()

# 📦 Pydantic schema for Wallet
class Wallet(BaseModel):
    user_id: str
    address: str
    balance: PositiveDecimal
    currency: str = Field(..., pattern="^(USD|ETH|BTC|USDC)$")

def generate_fake_wallets(user_ids: List[str], num_wallets_per_user: int = 2) -> List[Wallet]:
    """Generates fake wallet data."""
    wallets = []
    for user_id in user_ids:
        for _ in range(num_wallets_per_user):
            wallet = Wallet(
                user_id=user_id,
                address=fake.sha256(),
                balance=Decimal(str(round(random.uniform(100, 100000), 2))),
                currency=random.choice(["USD", "ETH", "BTC", "USDC"])
            )
            wallets.append(wallet)
    return wallets

def insert_fake_wallets(wallets: List[Wallet]) -> List[List[str]]:
    """Inserts fake wallet data into Supabase via supabase_bot."""
    wallet_ids = []
    for wallet in wallets:
        try:
            wallet_data = wallet.model_dump(exclude_none=True)
            wallet_data["balance"] = str(wallet_data["balance"])
            print(f"DEBUG: Attempting to upsert wallet_data: {wallet_data}")
            response = supabase_bot.table("wallets").upsert(wallet_data).execute()
            inserted = response.data[0]
            print(f"✅ Inserted wallet for user {inserted['user_id']}")
            wallet_ids.append([inserted['id'], inserted['user_id']])
        except Exception as e:
            print(f"❌ Exception while inserting wallet: {e}")
    return wallet_ids

if __name__ == "__main__":
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(3)]
    wallets_data = generate_fake_wallets(dummy_user_ids)
    insert_fake_wallets(wallets_data)
    print("🏁 Wallet data generation and insertion complete.")
