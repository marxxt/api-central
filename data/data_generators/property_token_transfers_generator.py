import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_property_token_transfers(property_ids, wallet_ids, num_transfers_per_property=2):
    """Generates fake property token transfer data."""
    property_transfers = []

    for prop_id in property_ids:
        for _ in range(num_transfers_per_property):
            from_wallet_id = random.choice(wallet_ids) if wallet_ids else None
            to_wallet_id = random.choice(wallet_ids) if wallet_ids else None
            
            # Ensure to_wallet_id is not None
            if not to_wallet_id:
                continue

            property_transfers.append({
                
                "property_id": prop_id,
                "from_wallet_id": from_wallet_id,
                "to_wallet_id": to_wallet_id,
                "tokens_transferred": random.randint(1, 500),
                "tx_hash": fake.sha256(),
                "timestamp": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            })
    return property_transfers

def insert_fake_property_token_transfers(conn, property_transfers):
    """Inserts fake property token transfer data."""
    cursor = conn.cursor()
    for transfer in property_transfers:
        try:
            cursor.execute(
                """
                INSERT INTO public.property_token_transfers (id, property_id, from_wallet_id, to_wallet_id, tokens_transferred, tx_hash, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    property_id = EXCLUDED.property_id,
                    from_wallet_id = EXCLUDED.from_wallet_id,
                    to_wallet_id = EXCLUDED.to_wallet_id,
                    tokens_transferred = EXCLUDED.tokens_transferred,
                    tx_hash = EXCLUDED.tx_hash,
                    timestamp = EXCLUDED.timestamp;
                """,
                (
                    transfer["id"], transfer["property_id"], transfer["from_wallet_id"],
                    transfer["to_wallet_id"], transfer["tokens_transferred"],
                    transfer["tx_hash"], transfer["timestamp"]
                )
            )
            print(f"Inserted property token transfer {transfer['id']} for property {transfer['property_id']}")
        except Error as e:
            print(f"Error inserting property token transfer {transfer['id']} for property {transfer['property_id']}: {e}")
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
            dummy_property_ids = [uuid.uuid4() for _ in range(3)]
            dummy_wallet_ids = [uuid.uuid4() for _ in range(5)]
            property_transfers_data = generate_fake_property_token_transfers(dummy_property_ids, dummy_wallet_ids)
            insert_fake_property_token_transfers(conn, property_transfers_data)
            print("Property Token Transfers data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")