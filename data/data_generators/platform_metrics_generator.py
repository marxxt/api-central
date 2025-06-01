import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_platform_metrics(entity_ids=None, num_metrics=10):
    """Generates fake platform metrics data."""
    platform_metrics = []
    metric_names = ['total_users', 'total_snfts', 'total_trades', 'daily_active_users', 'average_transaction_value']
    entities = ['platform', 'user']

    for _ in range(num_metrics):
        entity_type = random.choice(entities)
        entity_id = random.choice(entity_ids) if entity_type == 'user' and entity_ids else None
        metric_name = random.choice(metric_names)
        metric_value = round(random.uniform(100, 1000000), 2)

        platform_metrics.append({
            
            "entity": entity_type,
            "entity_id": entity_id,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "recorded_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
        })
    return platform_metrics

def insert_fake_platform_metrics(conn, platform_metrics):
    """Inserts fake platform metrics data."""
    cursor = conn.cursor()
    for metric in platform_metrics:
        try:
            cursor.execute(
                """
                INSERT INTO public.platform_metrics (id, entity, entity_id, metric_name, metric_value, recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    entity = EXCLUDED.entity,
                    entity_id = EXCLUDED.entity_id,
                    metric_name = EXCLUDED.metric_name,
                    metric_value = EXCLUDED.metric_value,
                    recorded_at = EXCLUDED.recorded_at;
                """,
                (metric["id"], metric["entity"], metric["entity_id"], metric["metric_name"], metric["metric_value"], metric["recorded_at"])
            )
            print(f"Inserted platform metric: {metric['metric_name']} for {metric['entity']}:{metric['entity_id']}")
        except Error as e:
            print(f"Error inserting platform metric {metric['metric_name']}: {e}")
            conn.rollback()
    conn.commit()
    cursor.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")

    def get_db_connection():
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable not set.")
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Error as e:
            print(f"Error connecting to the database: {e}")
            return None

    conn = None
    try:
        conn = get_db_connection()
        if conn:
            # Dummy data for testing independently
            dummy_entity_ids = [uuid.uuid4() for _ in range(5)] # Represents user_ids for 'user' entity type
            platform_metrics_data = generate_fake_platform_metrics(dummy_entity_ids)
            insert_fake_platform_metrics(conn, platform_metrics_data)
            print("Platform Metrics data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")