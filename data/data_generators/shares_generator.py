import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_shares(user_ids, asset_ids, num_shares_per_user=3):
    """Generates fake shares data."""
    shares = []
    asset_types = ['snft', 'post', 'property', 'bot_strategy']
    shared_with_options = ['public', 'followers'] # Could also include DAO IDs or specific user IDs

    for user_id in user_ids:
        for _ in range(num_shares_per_user):
            asset_type = random.choice(asset_types)
            asset_id = random.choice(asset_ids) if asset_ids else str(uuid.uuid4()) # Use dummy if no real asset_ids

            shares.append({
                
                "user_id": user_id,
                "asset_type": asset_type,
                "asset_id": str(asset_id),
                "shared_with": random.choice(shared_with_options),
                "comment": fake.sentence(nb_words=5) if random.random() > 0.5 else None,
                "shared_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            })
    return shares

def insert_fake_shares(conn, shares):
    """Inserts fake shares data."""
    cursor = conn.cursor()
    for share in shares:
        try:
            cursor.execute(
                """
                INSERT INTO public.shares (id, user_id, asset_type, asset_id, shared_with, comment, shared_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    asset_type = EXCLUDED.asset_type,
                    asset_id = EXCLUDED.asset_id,
                    shared_with = EXCLUDED.shared_with,
                    comment = EXCLUDED.comment,
                    shared_at = EXCLUDED.shared_at;
                """,
                (
                    share["id"], share["user_id"], share["asset_type"], share["asset_id"],
                    share["shared_with"], share["comment"], share["shared_at"]
                )
            )
            print(f"Inserted share {share['id']} by user {share['user_id']}")
        except Error as e:
            print(f"Error inserting share {share['id']} by user {share['user_id']}: {e}")
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
            dummy_user_ids = [uuid.uuid4() for _ in range(5)]
            dummy_asset_ids = [uuid.uuid4() for _ in range(10)] # Can be SNFT IDs, Property IDs, etc.
            shares_data = generate_fake_shares(dummy_user_ids, dummy_asset_ids)
            insert_fake_shares(conn, shares_data)
            print("Shares data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")