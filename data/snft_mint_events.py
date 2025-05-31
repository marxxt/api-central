import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_snft_mint_events(snft_ids, user_ids, num_events_per_snft=1):
    """Generates fake SNFT mint event data."""
    snft_mint_events = []
    statuses = ['confirmed', 'pending', 'failed']

    for snft_id in snft_ids:
        for _ in range(num_events_per_snft):
            user_id = random.choice(user_ids) if user_ids else None
            
            snft_mint_events.append({
                
                "snft_id": snft_id,
                "tx_hash": fake.sha256(),
                "user_id": user_id,
                "quantity": round(random.uniform(1, 1000), 2),
                "minted_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc),
                "status": random.choice(statuses)
            })
    return snft_mint_events

def insert_fake_snft_mint_events(conn, snft_mint_events):
    """Inserts fake SNFT mint event data."""
    cursor = conn.cursor()
    for event in snft_mint_events:
        try:
            cursor.execute(
                """
                INSERT INTO public.snft_mint_events (id, snft_id, tx_hash, user_id, quantity, minted_at, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    snft_id = EXCLUDED.snft_id,
                    tx_hash = EXCLUDED.tx_hash,
                    user_id = EXCLUDED.user_id,
                    quantity = EXCLUDED.quantity,
                    minted_at = EXCLUDED.minted_at,
                    status = EXCLUDED.status;
                """,
                (
                    event["id"], event["snft_id"], event["tx_hash"], event["user_id"],
                    event["quantity"], event["minted_at"], event["status"]
                )
            )
            print(f"Inserted SNFT mint event {event['id']} for SNFT {event['snft_id']}")
        except Error as e:
            print(f"Error inserting SNFT mint event {event['id']} for SNFT {event['snft_id']}: {e}")
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
            dummy_user_ids = [uuid.uuid4() for _ in range(3)]
            snft_mint_events_data = generate_fake_snft_mint_events(dummy_snft_ids, dummy_user_ids)
            insert_fake_snft_mint_events(conn, snft_mint_events_data)
            print("SNFT Mint Events data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")