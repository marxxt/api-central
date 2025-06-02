import uuid
import random
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
from faker import Faker
from db_utils import supabase_bot

fake = Faker()

class PlatformMetric(BaseModel):
    entity: str
    entity_id: Optional[str]
    metric_name: str
    metric_value: float
    recorded_at: datetime


def generate_fake_platform_metrics(entity_ids: List[str], num_metrics: int = 10) -> List[PlatformMetric]:
    metrics = []
    metric_names = ['total_users', 'total_snfts', 'total_trades', 'daily_active_users', 'average_transaction_value']
    entities = ['platform', 'user']

    for _ in range(num_metrics):
        entity_type = random.choice(entities)
        entity_id = random.choice(entity_ids)
        metric_name = random.choice(metric_names)
        metric_value = round(random.uniform(100, 1000000), 2)

        metrics.append(
            PlatformMetric(
                entity=entity_type,
                entity_id=entity_id,
                metric_name=metric_name,
                metric_value=metric_value,
                recorded_at=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            )
        )
    return metrics


def insert_fake_platform_metrics(metrics: List[PlatformMetric]) -> None:
    for metric in metrics:
        try:
            data = metric.model_dump()
            if isinstance(data["recorded_at"], datetime):
                data["recorded_at"] = data["recorded_at"].isoformat()
                
            # print("DATA", data)
            supabase_bot.table("platform_metrics").upsert(data).execute()
            print(f"✅ Inserted platform metric: {metric.metric_name} for {metric.entity}:{metric.entity_id}")
        except Exception as e:
            print(f"❌ Error inserting platform metric {metric.metric_name}: {e}")


if __name__ == "__main__":
    dummy_entity_ids = [str(uuid.uuid4()) for _ in range(5)]
    platform_metrics_data = generate_fake_platform_metrics(dummy_entity_ids)
    insert_fake_platform_metrics(platform_metrics_data)
    print("🏁 Platform Metrics data generation and insertion complete.")
