import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_property_token_ownership(property_ids, wallet_ids, num_ownerships_per_property=1):
    """Generates fake property token ownership data."""
    property_ownerships = []

    for prop_id in property_ids:
        for _ in range(num_ownerships_per_property):
            wallet_id = random.choice(wallet_ids) if wallet_ids else None
            if not wallet_id:
                continue

            property_ownerships.append({
                
                "property_id": prop_id,
                "wallet_id": wallet_id,
                "tokens_owned": random.randint(1, 10000)
            })
    return property_ownerships

def insert_fake_property_token_ownership(conn, property_ownerships):
    """Inserts fake property token ownership data."""
    cursor = conn.cursor()
    for ownership in property_ownerships:
        try:
            cursor.execute(
                """
                INSERT INTO public.property_token_ownership (id, property_id, wallet_id, tokens_owned, last_updated)
                VALUES (%s, %s, %s, %s, now())
                ON CONFLICT (property_id, wallet_id) DO UPDATE SET
                    tokens_owned = EXCLUDED.tokens_owned,
                    last_updated = now();
                """,
                (ownership["id"], ownership["property_id"], ownership["wallet_id"], ownership["tokens_owned"])
            )
            print(f"Inserted property token ownership for property {ownership['property_id']} by wallet {ownership['wallet_id']}")
        except Error as e:
            print(f"Error inserting property token ownership for property {ownership['property_id']} by wallet {ownership['wallet_id']}: {e}")
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
            dummy_wallet_ids = [uuid.uuid4() for _ in range(3)]
            property_ownership_data = generate_fake_property_token_ownership(dummy_property_ids, dummy_wallet_ids)
            insert_fake_property_token_ownership(conn, property_ownership_data)
            print("Property Token Ownership data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")