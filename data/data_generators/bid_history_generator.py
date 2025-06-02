import uuid
import random
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from faker import Faker
from db_utils import supabase_bot

fake = Faker()

class BidHistory(BaseModel):
    auction_id: str
    bidder: str
    amount: Decimal = Field(gt=0)
    time: datetime
    epoch_timestamp: int

    @field_validator("epoch_timestamp", mode="before")
    @classmethod
    def calc_epoch(cls, v, values):
        if not v and "time" in values:
            return int(values["time"].timestamp())
        return v

def generate_fake_bid_history(auction_ids: List[str], bidder_ids: List[str], num_bids_per_auction: int = 3) -> List[BidHistory]:
    """Generates fake bid history data."""
    bids = []
    for auction_id in auction_ids:
        for _ in range(num_bids_per_auction):
            bidder_id = random.choice(bidder_ids)
            bid_time = fake.date_time_between(start_date="-1m", end_date="now", tzinfo=timezone.utc)
            bids.append(BidHistory(
                auction_id=auction_id,
                bidder=bidder_id,
                amount=Decimal(str(round(random.uniform(100, 100000), 2))),
                time=bid_time,
                epoch_timestamp=int(bid_time.timestamp())
            ))
    return bids

def insert_fake_bid_history(bids: List[BidHistory]) -> None:
    for bid in bids:
        try:
            record = bid.model_dump()
            record["amount"] = str(record["amount"])
            record["id"] = str(uuid.uuid4())
            # Convert datetime object to ISO 8601 string
            if isinstance(record["time"], datetime):
                record["time"] = record["time"].isoformat()
            response = supabase_bot.table("bid_history").upsert(record).execute()
            print(f"✅ Inserted bid for auction {bid.auction_id} by bidder {bid.bidder}")
        except Exception as e:
            print(f"❌ Error inserting bid for auction {bid.auction_id} by bidder {bid.bidder}: {e}")

if __name__ == "__main__":
    dummy_auction_ids = [str(uuid.uuid4()) for _ in range(3)]
    dummy_bidder_ids = [str(uuid.uuid4()) for _ in range(3)]
    data = generate_fake_bid_history(dummy_auction_ids, dummy_bidder_ids)
    insert_fake_bid_history(data)
    print("🏁 Bid History data generation and insertion complete.")
