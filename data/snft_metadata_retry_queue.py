import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_snft_metadata_retry_queue(snft_ids, num_entries_per_snft=1):
    """Generates fake SNFT metadata retry queue data."""
    retry_queue_entries = []

    for snft_id in snft_ids:
        for _ in range(num_entries_per_snft):
            last_attempt = fake.date_time_between(start_date="-1m", end_date="now", tzinfo=timezone.utc)
            next_retry = last_attempt + timedelta(minutes=random.randint(5, 60))

            retry_queue_entries.append({
                
                "snft_id": snft_id,
                "retry_count": random.randint(1, 5),
                "last_attempt_at": last_attempt,
                "next_retry_at": next_retry,
                "error_log": fake.paragraph(nb_sentences=1)
            })
    return retry_queue_entries

def insert_fake_snft_metadata_retry_queue(conn, retry_queue_entries):
    """Inserts fake SNFT metadata retry queue data."""
    cursor = conn.cursor()
    for entry in retry_queue_entries:
        try:
            cursor.execute(
                """
                INSERT INTO public.snft_metadata_retry_queue (
                    id, snft_id, retry_count, last_attempt_at, next_retry_at, error_log, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (id) DO UPDATE SET
                    snft_id = EXCLUDED.snft_id,
                    retry_count = EXCLUDED.retry_count,
                    last_attempt_at = EXCLUDED.last_attempt_at,
                    next_retry_at = EXCLUDED.next_retry_at,
                    error_log = EXCLUDED.error_log;
                """,
                (
                    entry["id"], entry["snft_id"], entry["retry_count"],
                    entry["last_attempt_at"], entry["next_retry_at"], entry["error_log"]
                )
            )
            print(f"Inserted SNFT metadata retry queue entry {entry['id']} for SNFT {entry['snft_id']}")
        except Error as e:
            print(f"Error inserting SNFT metadata retry queue entry {entry['id']} for SNFT {entry['snft_id']}: {e}")
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
            retry_queue_data = generate_fake_snft_metadata_retry_queue(dummy_snft_ids)
            insert_fake_snft_metadata_retry_queue(conn, retry_queue_data)
            print("SNFT Metadata Retry Queue data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")