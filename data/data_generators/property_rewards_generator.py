import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_property_rewards(user_ids, badge_ids, property_ids, num_rewards_per_user=2):
    """Generates fake property rewards data."""
    property_rewards = []

    for user_id in user_ids:
        for _ in range(num_rewards_per_user):
            badge_id = random.choice(badge_ids) if badge_ids else None
            property_id = random.choice(property_ids) if property_ids else None
            
            if not property_id: # Property is a required FK
                continue

            valid_from = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            valid_to = valid_from + timedelta(days=random.randint(30, 365))

            property_rewards.append({
                
                "user_id": user_id,
                "badge_id": badge_id,
                "property_id": property_id,
                "nights_awarded": random.randint(1, 10),
                "nights_used": random.randint(0, 5),
                "valid_from": valid_from,
                "valid_to": valid_to
            })
    return property_rewards

def insert_fake_property_rewards(conn, property_rewards):
    """Inserts fake property rewards data."""
    cursor = conn.cursor()
    for reward in property_rewards:
        try:
            cursor.execute(
                """
                INSERT INTO public.property_rewards (
                    id, user_id, badge_id, property_id, nights_awarded,
                    nights_used, valid_from, valid_to, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    badge_id = EXCLUDED.badge_id,
                    property_id = EXCLUDED.property_id,
                    nights_awarded = EXCLUDED.nights_awarded,
                    nights_used = EXCLUDED.nights_used,
                    valid_from = EXCLUDED.valid_from,
                    valid_to = EXCLUDED.valid_to,
                    updated_at = now();
                """,
                (
                    reward["id"], reward["user_id"], reward["badge_id"], reward["property_id"],
                    reward["nights_awarded"], reward["nights_used"], reward["valid_from"],
                    reward["valid_to"]
                )
            )
            print(f"Inserted property reward {reward['id']} for user {reward['user_id']}")
        except Error as e:
            print(f"Error inserting property reward {reward['id']} for user {reward['user_id']}: {e}")
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
            dummy_badge_ids = [uuid.uuid4() for _ in range(3)]
            dummy_property_ids = [uuid.uuid4() for _ in range(5)]
            property_rewards_data = generate_fake_property_rewards(dummy_user_ids, dummy_badge_ids, dummy_property_ids)
            insert_fake_property_rewards(conn, property_rewards_data)
            print("Property Rewards data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")