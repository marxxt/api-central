import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_snft_events(snft_ids, num_events_per_snft=3):
    """Generates fake SNFT event data."""
    snft_events = []
    event_types = ['status_change', 'metadata_created', 'contract_deployed', 'transfer', 'listing']

    for snft_id in snft_ids:
        for _ in range(num_events_per_snft):
            event_type = random.choice(event_types)
            event_details = fake.json(num_rows=1, data_columns=[('old_value', 'word'), ('new_value', 'word')])

            snft_events.append({
                
                "snft_id": snft_id,
                "event_type": event_type,
                "event_details": event_details,
                "created_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            })
    return snft_events

def insert_fake_snft_events(conn, snft_events):
    """Inserts fake SNFT event data."""
    cursor = conn.cursor()
    for event in snft_events:
        try:
            cursor.execute(
                """
                INSERT INTO public.snft_events (id, snft_id, event_type, event_details, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    snft_id = EXCLUDED.snft_id,
                    event_type = EXCLUDED.event_type,
                    event_details = EXCLUDED.event_details,
                    created_at = EXCLUDED.created_at;
                """,
                (event["id"], event["snft_id"], event["event_type"], event["event_details"], event["created_at"])
            )
            print(f"Inserted SNFT event {event['id']} for SNFT {event['snft_id']}")
        except Error as e:
            print(f"Error inserting SNFT event {event['id']} for SNFT {event['snft_id']}: {e}")
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
            dummy_snft_ids = [uuid.uuid4() for _ in range(5)]
            snft_events_data = generate_fake_snft_events(dummy_snft_ids)
            insert_fake_snft_events(conn, snft_events_data)
            print("SNFT Events data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")