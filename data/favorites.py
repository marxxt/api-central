import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_favorites(user_ids, asset_ids, num_favorites_per_user=5):
    """Generates fake favorites data."""
    favorites = []
    asset_types = ['snft', 'post', 'user', 'property', 'bot_strategy', 'chat_message']

    for user_id in user_ids:
        # Ensure unique favorites per user for a given asset type and ID
        for _ in range(num_favorites_per_user):
            asset_type = random.choice(asset_types)
            asset_id = random.choice(asset_ids) if asset_ids else str(uuid.uuid4()) # Use dummy if no real asset_ids

            favorites.append({
                
                "user_id": user_id,
                "asset_type": asset_type,
                "asset_id": str(asset_id), # Ensure asset_id is string for text column
                "favorited_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            })
    return favorites

def insert_fake_favorites(conn, favorites):
    """Inserts fake favorites data."""
    cursor = conn.cursor()
    for fav in favorites:
        try:
            cursor.execute(
                """
                INSERT INTO public.favorites (id, user_id, asset_type, asset_id, favorited_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id, asset_type, asset_id) DO UPDATE SET
                    favorited_at = EXCLUDED.favorited_at;
                """,
                (fav["id"], fav["user_id"], fav["asset_type"], fav["asset_id"], fav["favorited_at"])
            )
            print(f"Inserted favorite for user {fav['user_id']} on {fav['asset_type']}:{fav['asset_id']}")
        except Error as e:
            print(f"Error inserting favorite for user {fav['user_id']} on {fav['asset_type']}:{fav['asset_id']}: {e}")
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
            favorites_data = generate_fake_favorites(dummy_user_ids, dummy_asset_ids)
            insert_fake_favorites(conn, favorites_data)
            print("Favorites data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")