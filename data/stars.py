import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_stars(user_ids, entity_ids, num_stars_per_user=3):
    """Generates fake star (rating) data."""
    stars = []
    entity_types = ['user', 'dao', 'snft']

    for user_id in user_ids:
        # Ensure unique ratings per user for a given entity
        rated_entities = random.sample(entity_ids, min(num_stars_per_user, len(entity_ids)))
        for entity_id in rated_entities:
            stars.append({
                
                "user_id": user_id,
                "entity_type": random.choice(entity_types),
                "entity_id": entity_id,
                "value": random.randint(1, 5),
                "review": fake.sentence() if random.random() > 0.3 else None,
                "created_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            })
    return stars

def insert_fake_stars(conn, stars):
    """Inserts fake star (rating) data."""
    cursor = conn.cursor()
    for star in stars:
        try:
            cursor.execute(
                """
                INSERT INTO public.stars (id, user_id, entity_type, entity_id, value, review, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (user_id, entity_type, entity_id) DO UPDATE SET
                    value = EXCLUDED.value,
                    review = EXCLUDED.review,
                    updated_at = now();
                """,
                (star["id"], star["user_id"], star["entity_type"], star["entity_id"], star["value"], star["review"], star["created_at"])
            )
            print(f"Inserted star {star['value']} for {star['entity_type']}:{star['entity_id']} by user {star['user_id']}")
        except Error as e:
            print(f"Error inserting star for {star['entity_type']}:{star['entity_id']} by user {star['user_id']}: {e}")
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
            dummy_entity_ids = [uuid.uuid4() for _ in range(10)] # Can be User IDs, DAO IDs, SNFT IDs
            stars_data = generate_fake_stars(dummy_user_ids, dummy_entity_ids)
            insert_fake_stars(conn, stars_data)
            print("Stars data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")