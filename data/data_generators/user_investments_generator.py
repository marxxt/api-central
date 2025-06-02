import uuid
import random
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, Field
from faker import Faker
from db_utils import supabase_bot

fake = Faker()

class UserInvestment(BaseModel):
    user_id: str
    property_asset_id: str
    tokens_owned: float
    avg_buy_price_per_token: float
    avg_buy_price_currency: str
    purchase_date: datetime
    status: str

def generate_fake_user_investments(user_ids: List[str], property_asset_ids: List[List[str]], num_investments_per_user: int = 2) -> List[UserInvestment]:
    statuses = ['Owned', 'Staked', 'ListedForSale', 'InBot']
    currencies = ["USDC", "ETH", "BTC"]
    investments = []

    for user_id in user_ids:
        for _ in range(num_investments_per_user):
            # property_asset_ids is List[List[str]], where inner list is [property_id, user_id]
            # We need to select a property_id
            property_asset_id = random.choice([p[0] for p in property_asset_ids]) if property_asset_ids else None
            if not property_asset_id:
                continue

            investments.append(
                UserInvestment(
                    user_id=user_id,
                    property_asset_id=property_asset_id,
                    tokens_owned=round(random.uniform(1, 1000), 2),
                    avg_buy_price_per_token=round(random.uniform(0.1, 100), 2),
                    avg_buy_price_currency=random.choice(currencies),
                    purchase_date=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc),
                    status=random.choice(statuses)
                )
            )
    return investments

def insert_fake_user_investments(investments: List[UserInvestment]) -> None:
    for inv in investments:
        try:
            data = inv.model_dump()
            data["id"] = str(uuid.uuid4())
            data["created_at"] = datetime.now(timezone.utc).isoformat()
            data["updated_at"] = datetime.now(timezone.utc).isoformat()
            # Convert purchase_date to ISO 8601 string
            if isinstance(data["purchase_date"], datetime):
                data["purchase_date"] = data["purchase_date"].isoformat()
            supabase_bot.table("user_investments").upsert(data).execute()
            print(f"✅ Inserted investment for user {inv.user_id} in asset {inv.property_asset_id}")
        except Exception as e:
            print(f"❌ Error inserting investment for user {inv.user_id}: {e}")

if __name__ == "__main__":
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(3)]
    dummy_property_asset_ids = [[str(uuid.uuid4())] for _ in range(3)]
    data = generate_fake_user_investments(dummy_user_ids, dummy_property_asset_ids)
    insert_fake_user_investments(data)
    print("🏁 User Investments insertion complete.")
