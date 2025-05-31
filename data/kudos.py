import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_kudos(from_user_ids, to_user_ids, num_kudos_per_user=3):
    """Generates fake kudos data."""
    kudos_records = []
    context_types = ['chat_message', 'comment', 'post', 'proposal', 'strategy']

    for from_user_id in from_user_ids:
        # Ensure unique kudos from a user in a given context
        for _ in range(num_kudos_per_user):
            to_user_id = random.choice(to_user_ids) if to_user_ids else None
            if not to_user_id or from_user_id == to_user_id: # Prevent self-kudos
                continue

            context_type = random.choice(context_types)
            context_id = str(uuid.uuid4()) # Dummy context ID

            kudos_records.append({
                
                "from_user_id": from_user_id,
                "to_user_id": to_user_id,
                "context_type": context_type,
                "context_id": context_id,
                "reason": fake.sentence(nb_words=4) if random.random() > 0.3 else None,
                "value": random.randint(1, 5),
                "created_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            })
    return kudos_records

def insert_fake_kudos(conn, kudos_records):
    """Inserts fake kudos data."""
    cursor = conn.cursor()
    for kudos in kudos_records:
        try:
            cursor.execute(
                """
                INSERT INTO public.kudos (id, from_user_id, to_user_id, context_type, context_id, reason, value, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (from_user_id, context_type, context_id) DO UPDATE SET
                    to_user_id = EXCLUDED.to_user_id,
                    reason = EXCLUDED.reason,
                    value = EXCLUDED.value,
                    created_at = EXCLUDED.created_at;
                """,
                (
                    kudos["id"], kudos["from_user_id"], kudos["to_user_id"],
                    kudos["context_type"], kudos["context_id"], kudos["reason"],
                    kudos["value"], kudos["created_at"]
                )
            )
            print(f"Inserted kudos from {kudos['from_user_id']} to {kudos['to_user_id']} for {kudos['context_type']}:{kudos['context_id']}")
        except Error as e:
            print(f"Error inserting kudos from {kudos['from_user_id']} to {kudos['to_user_id']} for {kudos['context_type']}:{kudos['context_id']}: {e}")
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
            dummy_from_user_ids = [uuid.uuid4() for _ in range(5)]
            dummy_to_user_ids = [uuid.uuid4() for _ in range(5)]
            kudos_data = generate_fake_kudos(dummy_from_user_ids, dummy_to_user_ids)
            insert_fake_kudos(conn, kudos_data)
            print("Kudos data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")