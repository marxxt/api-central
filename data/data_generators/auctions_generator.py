import uuid
import random
from decimal import Decimal
from datetime import timedelta, timezone
from faker import Faker
from typing import Annotated, List
from pydantic import BaseModel, Field
from pydantic.types import condecimal
from db_utils import supabase_bot

PositiveDecimal = Annotated[condecimal(gt=0), Field(description="Decimal value greater than 0")]

fake = Faker()

# 🎯 Pydantic schema for Auction
class Auction(BaseModel):
    property_id: str
    seller_id: str
    type: str = Field(..., pattern="^(Whole Project|Individual Tokens)$")
    status: str = Field(..., pattern="^(active|pending|closed|completed)$")
    start_time: str
    end_time: str
    starting_price: PositiveDecimal

def generate_fake_auctions(property_ids: List[List[str]], seller_ids: List[str], num_auctions_per_property=1) -> List[Auction]:
    auctions = []
    for prop_id in property_ids:
        for _ in range(num_auctions_per_property):
            seller_id = random.choice(seller_ids) if seller_ids else prop_id[1]
            start_time = fake.date_time_between(start_date="-1m", end_date="now", tzinfo=timezone.utc)
            end_time = start_time + timedelta(days=random.randint(1, 30))
            auction = Auction(
                property_id=prop_id[0],
                seller_id=seller_id,
                type=random.choice(["Whole Project", "Individual Tokens"]),
                status=random.choice(["active", "pending", "closed", "completed"]),
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                starting_price=Decimal(str(round(random.uniform(1_000, 1_000_000), 2)))
            )
            auctions.append(auction)
    return auctions

def insert_fake_auctions(auctions: List[Auction]) -> List[str]:
    auction_ids = []
    for auction in auctions:
        try:
            data = auction.model_dump()
            data["starting_price"] = str(data["starting_price"])
            response = supabase_bot.table("auctions").upsert(data).execute()
            inserted = response.data[0]
            print(f"🏷️ Inserted auction for property {inserted['property_id']} with id: {inserted['id']}")
            auction_ids.append(inserted["id"])
        except Exception as e:
            print(f"❌ Error inserting auction: {e}")
    return auction_ids

if __name__ == "__main__":
    pass
