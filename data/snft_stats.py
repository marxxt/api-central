import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_snft_stats(snft_ids):
    """Generates fake SNFT stats data."""
    snft_stats = []

    for snft_id in snft_ids:
        snft_stats.append({
            "snft_id": snft_id,
            "favorite_count": random.randint(0, 200),
            "star_count": random.randint(0, 100),
            "average_rating": round(random.uniform(1.0, 5.0), 2),
            "comment_count": random.randint(0, 150),
            "mention_count": random.randint(0, 50),
            "share_count": random.randint(0, 75),
            "last_updated": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
        })
    return snft_stats

def insert_fake_snft_stats(conn, snft_stats):
    """Inserts fake SNFT stats data."""
    cursor = conn.cursor()
    for stats in snft_stats:
        try:
            cursor.execute(
                """
                INSERT INTO public.snft_stats (
                    snft_id, favorite_count, star_count, average_rating,
                    comment_count, mention_count, share_count, last_updated
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (snft_id) DO UPDATE SET
                    favorite_count = EXCLUDED.favorite_count,
                    star_count = EXCLUDED.star_count,
                    average_rating = EXCLUDED.average_rating,
                    comment_count = EXCLUDED.comment_count,
                    mention_count = EXCLUDED.mention_count,
                    share_count = EXCLUDED.share_count,
                    last_updated = EXCLUDED.last_updated;
                """,
                (
                    stats["snft_id"], stats["favorite_count"], stats["star_count"],
                    stats["average_rating"], stats["comment_count"], stats["mention_count"],
                    stats["share_count"], stats["last_updated"]
                )
            )
            print(f"Inserted SNFT stats for SNFT {stats['snft_id']}")
        except Error as e:
            print(f"Error inserting SNFT stats for SNFT {stats['snft_id']}: {e}")
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
            dummy_snft_ids = [uuid.uuid4() for _ in range(5)]
            snft_stats_data = generate_fake_snft_stats(dummy_snft_ids)
            insert_fake_snft_stats(conn, snft_stats_data)
            print("SNFT Stats data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")