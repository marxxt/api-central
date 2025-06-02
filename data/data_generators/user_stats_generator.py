import uuid
import random
from datetime import datetime, timezone
from typing import List
from pydantic import BaseModel, Field
from faker import Faker
from db_utils import supabase_bot

fake = Faker()

class UserStat(BaseModel):
    user_id: str
    snft_count: int
    trade_count: int
    wallet_count: int
    comment_count: int
    reply_count: int
    share_count: int
    mention_count: int
    favorite_count: int
    star_count: int
    received_star_count: int
    average_rating: float = Field(..., ge=1.0, le=5.0)
    last_updated: datetime
    xp: int
    activity_streak: int
    last_action_date: datetime
    rank: str
    last_active: datetime

def generate_fake_user_stats(user_ids: List[str]) -> List[UserStat]:
    ranks = ['SSS', 'SS', 'S', 'A', 'B', 'C', 'D', 'F']
    return [
        UserStat(
            user_id=user_id,
            snft_count=random.randint(0, 100),
            trade_count=random.randint(0, 500),
            wallet_count=random.randint(1, 5),
            comment_count=random.randint(0, 200),
            reply_count=random.randint(0, 100),
            share_count=random.randint(0, 150),
            mention_count=random.randint(0, 75),
            favorite_count=random.randint(0, 100),
            star_count=random.randint(0, 50),
            received_star_count=random.randint(0, 200),
            average_rating=round(random.uniform(1.0, 5.0), 2),
            last_updated=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc),
            xp=random.randint(0, 10000),
            activity_streak=random.randint(0, 30),
            last_action_date=fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc),
            rank=random.choice(ranks),
            last_active=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
        )
        for user_id in user_ids
    ]

def insert_fake_user_stats(stats: List[UserStat]) -> None:
    for stat in stats:
        try:
            data = stat.model_dump()
            # print("DATA", data)
            if isinstance(data["last_updated"], datetime):
                data["last_updated"] = data["last_updated"].isoformat()

            if isinstance(data["last_action_date"], datetime):
                data["last_action_date"] = data["last_action_date"].isoformat()
                
            if isinstance(data["last_active"], datetime):
                data["last_active"] = data["last_active"].isoformat()
                
            supabase_bot.table("user_stats").upsert(data).execute()
            print(f"✅ Inserted stats for user {stat.user_id}")
        except Exception as e:
            print(f"❌ Error inserting stats for user {stat.user_id}: {e}")

if __name__ == "__main__":
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(5)]
    stats = generate_fake_user_stats(dummy_user_ids)
    insert_fake_user_stats(stats)
    print("🏁 User stats insertion complete.")
