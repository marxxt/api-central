import uuid
import random
from datetime import datetime, timezone
from typing import List, Tuple
from pydantic import BaseModel, Field
from faker import Faker
from db_utils import supabase_bot

fake = Faker()

class SNFTStat(BaseModel):
    snft_id: str
    favorite_count: int
    star_count: int
    average_rating: float = Field(..., ge=1.0, le=5.0)
    comment_count: int
    mention_count: int
    share_count: int
    last_updated: datetime

def generate_fake_snft_stats(snft_ids: List[Tuple[str, str, str]]) -> List[SNFTStat]:
    return [
        SNFTStat(
            snft_id=snft_id[0],
            favorite_count=random.randint(0, 200),
            star_count=random.randint(0, 100),
            average_rating=round(random.uniform(1.0, 5.0), 2),
            comment_count=random.randint(0, 150),
            mention_count=random.randint(0, 50),
            share_count=random.randint(0, 75),
            last_updated=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
        )
        for snft_id in snft_ids
    ]

def insert_fake_snft_stats(stats: List[SNFTStat]) -> None:
    for stat in stats:
        try:
            data = stat.model_dump()
            if isinstance(data["last_updated"], datetime):
                data["last_updated"] = data["last_updated"].isoformat()
            supabase_bot.table("snft_stats").upsert(data).execute()
            print(f"✅ Inserted SNFT stats for SNFT {stat.snft_id}")
        except Exception as e:
            print(f"❌ Error inserting SNFT stats for SNFT {stat.snft_id}: {e}")

if __name__ == "__main__":
    pass
