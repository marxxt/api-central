import uuid
import random
from datetime import datetime, timezone
from typing import List, Tuple
from pydantic import BaseModel, Field
from faker import Faker
from db_utils import supabase_bot

fake = Faker()

class Transaction(BaseModel):
    user_id: str
    snft_id: str # Added snft_id as per schema
    amount: float
    asset_type: str = Field(..., pattern="^(TRANSFER|LISTED|LISTING_CANCEL|AUCTIONED|AUCTION_CANCEL|BID_REGISTERED|BID_ACCEPTED)$")
    transaction_type: str = Field(..., pattern="^(BUY|SELL|TRANSFER|EXCHANGE|MINT|OTHER|UNKNOWN)$")
    status: str = Field(..., pattern="^(pending|completed|failed|cancelled)$")
    timestamp: datetime

def generate_fake_transactions(assets: List[Tuple[str, str, str]], count: int = 20) -> List[Transaction]:
    transactions = []
    for _ in range(count):
        snft_id, __, user_id = random.choice(assets)
        tx = Transaction(
            user_id=user_id, # Changed to use the current user_id from the loop
            snft_id=snft_id, # Added missing comma
            amount=round(random.uniform(10.0, 10000.0), 2),
            asset_type=random.choice(['TRANSFER',
                'LISTED',
                'LISTING_CANCEL',
                'AUCTIONED',
                'AUCTION_CANCEL',
                'BID_REGISTERED',
                'BID_ACCEPTED'
            ]),
            transaction_type=random.choice(['BUY', 'SELL', 'TRANSFER', 'EXCHANGE', 'MINT', 'OTHER', 'UNKNOWN']),
            status=random.choice(['pending', 'completed', 'failed', 'cancelled']),
            timestamp=fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc)
        ) # Added missing closing parenthesis for Transaction constructor
        transactions.append(tx)
    return transactions
   
    # snft_id uuid REFERENCES public.snfts(id) ON DELETE CASCADE NOT NULL,
    # user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL, -- Added user_id column
    # transaction_type text NOT NULL CHECK (transaction_type IN ('BUY', 'SELL', 'TRANSFER', 'EXCHANGE', 'MINT', 'OTHER', 'UNKNOWN')),
    # asset_type text, -- Added asset_type column
    # amount numeric,
    # status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'failed', 'cancelled')), -- Added status column
    # timestamp timestamp with time zone DEFAULT now(),

    # created_at timestamp with time zone DEFAULT now(),
    # updated_at 

def insert_fake_transactions(transactions: List[Transaction]) -> None:
   
    for tx in transactions:
        try:
            data = tx.model_dump()
            
            # Convert datetime object to ISO 8601 string
            if isinstance(data["timestamp"], datetime):
                data["timestamp"] = data["timestamp"].isoformat()
            
            print("DATA", data)
            supabase_bot.table("transactions").upsert(data).execute()
            print(f"✅ Inserted transaction for user {tx.user_id}")
        except Exception as e:
            print(f"❌ Error inserting transaction for user {tx.user_id}: {e}")

if __name__ == "__main__":
    pass
