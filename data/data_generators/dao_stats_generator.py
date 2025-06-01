import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_dao_stats(dao_ids):
    """Generates fake DAO stats data."""
    dao_stats = []

    for dao_id in dao_ids:
        dao_stats.append({
            "dao_id": dao_id,
            "snft_count": random.randint(0, 100),
            "comment_count": random.randint(0, 200),
            "share_count": random.randint(0, 150),
            "star_count": random.randint(0, 50),
            "received_star_count": random.randint(0, 200),
            "average_rating": round(random.uniform(1.0, 5.0), 2),
            "last_updated": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
        })
    return dao_stats

def insert_fake_dao_stats(conn, dao_stats):
    """Inserts fake DAO stats data."""
    cursor = conn.cursor()
    for stats in dao_stats:
        try:
            cursor.execute(
                """
                INSERT INTO public.dao_stats (
                    dao_id, snft_count, comment_count, share_count, star_count,
                    received_star_count, average_rating, last_updated
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (dao_id) DO UPDATE SET
                    snft_count = EXCLUDED.snft_count,
                    comment_count = EXCLUDED.comment_count,
                    share_count = EXCLUDED.share_count,
                    star_count = EXCLUDED.star_count,
                    received_star_count = EXCLUDED.received_star_count,
                    average_rating = EXCLUDED.average_rating,
                    last_updated = EXCLUDED.last_updated;
                """,
                (
                    stats["dao_id"], stats["snft_count"], stats["comment_count"],
                    stats["share_count"], stats["star_count"], stats["received_star_count"],
                    stats["average_rating"], stats["last_updated"]
                )
            )
            print(f"Inserted DAO stats for DAO {stats['dao_id']}")
        except Error as e:
            print(f"Error inserting DAO stats for DAO {stats['dao_id']}: {e}")
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
            dummy_dao_ids = [uuid.uuid4() for _ in range(5)]
            dao_stats_data = generate_fake_dao_stats(dummy_dao_ids)
            insert_fake_dao_stats(conn, dao_stats_data)
            print("DAO Stats data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")