import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_bid_history(auction_ids, bidder_ids, num_bids_per_auction=3):
    """Generates fake bid history data."""
    bid_history_records = []

    for auction_id in auction_ids:
        for _ in range(num_bids_per_auction):
            bidder_id = random.choice(bidder_ids) if bidder_ids else None
            if not bidder_id:
                continue

            bid_time = fake.date_time_between(start_date="-1m", end_date="now", tzinfo=timezone.utc)
            epoch_timestamp = int(bid_time.timestamp())

            bid_history_records.append({
                
                "auction_id": auction_id,
                "bidder": bidder_id,
                "amount": round(random.uniform(100, 100000), 2),
                "time": bid_time,
                "epoch_timestamp": epoch_timestamp
            })
    return bid_history_records

def insert_fake_bid_history(conn, bid_history_records):
    """Inserts fake bid history data."""
    cursor = conn.cursor()
    for record in bid_history_records:
        try:
            cursor.execute(
                """
                INSERT INTO public.bid_history (id, auction_id, bidder, amount, time, epoch_timestamp, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    auction_id = EXCLUDED.auction_id,
                    bidder = EXCLUDED.bidder,
                    amount = EXCLUDED.amount,
                    time = EXCLUDED.time,
                    epoch_timestamp = EXCLUDED.epoch_timestamp,
                    updated_at = now();
                """,
                (record["id"], record["auction_id"], record["bidder"], record["amount"], record["time"], record["epoch_timestamp"])
            )
            print(f"Inserted bid for auction {record['auction_id']} by bidder {record['bidder']}")
        except Error as e:
            print(f"Error inserting bid for auction {record['auction_id']} by bidder {record['bidder']}: {e}")
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
            dummy_auction_ids = [uuid.uuid4() for _ in range(3)]
            dummy_bidder_ids = [uuid.uuid4() for _ in range(3)]
            bid_history_data = generate_fake_bid_history(dummy_auction_ids, dummy_bidder_ids)
            insert_fake_bid_history(conn, bid_history_data)
            print("Bid History data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")