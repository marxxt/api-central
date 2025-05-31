import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_mentions(user_ids, dao_ids, snft_ids, num_mentions=10):
    """Generates fake mentions data."""
    mentions = []
    context_types = ['chat_message', 'comment', 'post', 'proposal']
    mentioned_types = ['user', 'dao', 'snft']

    all_possible_mentioned_ids = {
        'user': user_ids,
        'dao': dao_ids,
        'snft': snft_ids
    }

    for _ in range(num_mentions):
        mentioned_by_id = random.choice(user_ids) if user_ids else None
        if not mentioned_by_id:
            continue

        context_type = random.choice(context_types)
        context_id = str(uuid.uuid4()) # Dummy context ID

        mentioned_type = random.choice(mentioned_types)
        mentioned_id_list = all_possible_mentioned_ids.get(mentioned_type, [])
        mentioned_id = random.choice(mentioned_id_list) if mentioned_id_list else None

        if not mentioned_id:
            continue

        mentions.append({
            
            "context_type": context_type,
            "context_id": context_id,
            "mentioned_type": mentioned_type,
            "mentioned_id": mentioned_id,
            "mentioned_by": mentioned_by_id,
            "context_url": fake.url(),
            "created_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
        })
    return mentions

def insert_fake_mentions(conn, mentions):
    """Inserts fake mentions data."""
    cursor = conn.cursor()
    for mention in mentions:
        try:
            cursor.execute(
                """
                INSERT INTO public.mentions (
                    id, context_type, context_id, mentioned_type, mentioned_id,
                    mentioned_by, context_url, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    context_type = EXCLUDED.context_type,
                    context_id = EXCLUDED.context_id,
                    mentioned_type = EXCLUDED.mentioned_type,
                    mentioned_id = EXCLUDED.mentioned_id,
                    mentioned_by = EXCLUDED.mentioned_by,
                    context_url = EXCLUDED.context_url,
                    created_at = EXCLUDED.created_at;
                """,
                (
                    mention["id"], mention["context_type"], mention["context_id"],
                    mention["mentioned_type"], mention["mentioned_id"],
                    mention["mentioned_by"], mention["context_url"], mention["created_at"]
                )
            )
            print(f"Inserted mention {mention['id']} by {mention['mentioned_by']} of {mention['mentioned_type']}:{mention['mentioned_id']}")
        except Error as e:
            print(f"Error inserting mention {mention['id']} by {mention['mentioned_by']} of {mention['mentioned_type']}:{mention['mentioned_id']}: {e}")
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
            dummy_dao_ids = [uuid.uuid4() for _ in range(3)]
            dummy_snft_ids = [uuid.uuid4() for _ in range(7)]
            mentions_data = generate_fake_mentions(dummy_user_ids, dummy_dao_ids, dummy_snft_ids)
            insert_fake_mentions(conn, mentions_data)
            print("Mentions data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")