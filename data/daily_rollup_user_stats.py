import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_daily_rollup_user_stats(user_ids, num_days=30):
    """Generates fake daily rollup user stats data."""
    daily_stats = []

    for user_id in user_ids:
        for i in range(num_days):
            stat_date = datetime.now(timezone.utc).date() - timedelta(days=i)
            daily_stats.append({
                
                "user_id": user_id,
                "date": stat_date,
                "snft_count": random.randint(0, 50),
                "trade_count": random.randint(0, 200),
                "wallet_count": random.randint(1, 3),
                "comment_count": random.randint(0, 50),
                "reply_count": random.randint(0, 20),
                "share_count": random.randint(0, 30),
                "favorite_count": random.randint(0, 40),
                "star_count": random.randint(0, 20),
                "received_star_count": random.randint(0, 50),
                "average_rating": round(random.uniform(1.0, 5.0), 2)
            })
    return daily_stats

def insert_fake_daily_rollup_user_stats(conn, daily_stats):
    """Inserts fake daily rollup user stats data."""
    cursor = conn.cursor()
    for stats in daily_stats:
        try:
            cursor.execute(
                """
                INSERT INTO public.daily_rollup_user_stats (
                    id, user_id, date, snft_count, trade_count, wallet_count,
                    comment_count, reply_count, share_count, favorite_count,
                    star_count, received_star_count, average_rating, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (user_id, date) DO UPDATE SET
                    snft_count = EXCLUDED.snft_count,
                    trade_count = EXCLUDED.trade_count,
                    wallet_count = EXCLUDED.wallet_count,
                    comment_count = EXCLUDED.comment_count,
                    reply_count = EXCLUDED.reply_count,
                    share_count = EXCLUDED.share_count,
                    favorite_count = EXCLUDED.favorite_count,
                    star_count = EXCLUDED.star_count,
                    received_star_count = EXCLUDED.received_star_count,
                    average_rating = EXCLUDED.average_rating,
                    updated_at = now();
                """,
                (
                    stats["id"], stats["user_id"], stats["date"], stats["snft_count"],
                    stats["trade_count"], stats["wallet_count"], stats["comment_count"],
                    stats["reply_count"], stats["share_count"], stats["favorite_count"],
                    stats["star_count"], stats["received_star_count"], stats["average_rating"]
                )
            )
            print(f"Inserted daily rollup stats for user {stats['user_id']} on {stats['date']}")
        except Error as e:
            print(f"Error inserting daily rollup stats for user {stats['user_id']} on {stats['date']}: {e}")
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
            daily_rollup_data = generate_fake_daily_rollup_user_stats(dummy_user_ids)
            insert_fake_daily_rollup_user_stats(conn, daily_rollup_data)
            print("Daily Rollup User Stats data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")