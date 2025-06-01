import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_comments(user_ids, asset_ids, num_comments_per_asset=3, max_replies=2):
    """Generates fake comment data, including replies."""
    comments = []
    asset_types = ['snft', 'post', 'property', 'bot_strategy', 'chat_message']

    for asset_id in asset_ids:
        for _ in range(num_comments_per_asset):
            user_id = random.choice(user_ids) if user_ids else None
            if not user_id:
                continue

            # Top-level comment
            comment_id = uuid.uuid4()
            comments.append({
                "id": comment_id,
                "user_id": user_id,
                "asset_type": random.choice(asset_types),
                "asset_id": str(asset_id),
                "parent_id": None,
                "content": fake.paragraph(nb_sentences=2),
                "is_edited": fake.boolean(chance_of_getting_true=10),
                "created_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            })

            # Replies to this comment
            if max_replies > 0 and random.random() > 0.5: # 50% chance of having replies
                num_actual_replies = random.randint(1, max_replies)
                for _ in range(num_actual_replies):
                    reply_user_id = random.choice(user_ids) if user_ids else None
                    if not reply_user_id:
                        continue
                    comments.append({
                        
                        "user_id": reply_user_id,
                        "asset_type": comments[-1]["asset_type"], # Same asset type as parent
                        "asset_id": comments[-1]["asset_id"],     # Same asset ID as parent
                        "parent_id": comment_id,
                        "content": fake.sentence(),
                        "is_edited": fake.boolean(chance_of_getting_true=5),
                        "created_at": fake.date_time_between(start_date=comments[-1]["created_at"], end_date="now", tzinfo=timezone.utc)
                    })
    return comments

def insert_fake_comments(conn, comments):
    """Inserts fake comment data."""
    cursor = conn.cursor()
    for comment in comments:
        try:
            cursor.execute(
                """
                INSERT INTO public.comments (id, user_id, asset_type, asset_id, parent_id, content, is_edited, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    asset_type = EXCLUDED.asset_type,
                    asset_id = EXCLUDED.asset_id,
                    parent_id = EXCLUDED.parent_id,
                    content = EXCLUDED.content,
                    is_edited = EXCLUDED.is_edited,
                    created_at = EXCLUDED.created_at,
                    updated_at = now();
                """,
                (
                    comment["id"], comment["user_id"], comment["asset_type"], comment["asset_id"],
                    comment["parent_id"], comment["content"], comment["is_edited"], comment["created_at"]
                )
            )
            print(f"Inserted comment {comment['id']} by user {comment['user_id']}")
        except Error as e:
            print(f"Error inserting comment {comment['id']} by user {comment['user_id']}: {e}")
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
            dummy_asset_ids = [uuid.uuid4() for _ in range(3)] # Can be SNFT IDs, Property IDs, etc.
            comments_data = generate_fake_comments(dummy_user_ids, dummy_asset_ids)
            insert_fake_comments(conn, comments_data)
            print("Comments data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")