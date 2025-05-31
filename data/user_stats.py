import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_user_stats(user_ids):
    """Generates fake user stats data."""
    user_stats = []
    ranks = ['SSS', 'SS', 'S', 'A', 'B', 'C', 'D', 'F']

    for user_id in user_ids:
        user_stats.append({
            "user_id": user_id,
            "snft_count": random.randint(0, 100),
            "trade_count": random.randint(0, 500),
            "wallet_count": random.randint(1, 5),
            "comment_count": random.randint(0, 200),
            "reply_count": random.randint(0, 100),
            "share_count": random.randint(0, 150),
            "mention_count": random.randint(0, 75),
            "favorite_count": random.randint(0, 100),
            "star_count": random.randint(0, 50),
            "received_star_count": random.randint(0, 200),
            "average_rating": round(random.uniform(1.0, 5.0), 2),
            "last_updated": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc),
            "xp": random.randint(0, 10000),
            "activity_streak": random.randint(0, 30),
            "last_action_date": fake.date_between(start_date="-1y", end_date="today"),
            "rank": random.choice(ranks),
            "last_active": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
        })
    return user_stats

def insert_fake_user_stats(conn, user_stats):
    """Inserts fake user stats data."""
    cursor = conn.cursor()
    for stats in user_stats:
        try:
            cursor.execute(
                """
                INSERT INTO public.user_stats (
                    user_id, snft_count, trade_count, wallet_count, comment_count,
                    reply_count, share_count, mention_count, favorite_count, star_count,
                    received_star_count, average_rating, last_updated, xp, activity_streak,
                    last_action_date, rank, last_active
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    snft_count = EXCLUDED.snft_count,
                    trade_count = EXCLUDED.trade_count,
                    wallet_count = EXCLUDED.wallet_count,
                    comment_count = EXCLUDED.comment_count,
                    reply_count = EXCLUDED.reply_count,
                    share_count = EXCLUDED.share_count,
                    mention_count = EXCLUDED.mention_count,
                    favorite_count = EXCLUDED.favorite_count,
                    star_count = EXCLUDED.star_count,
                    received_star_count = EXCLUDED.received_star_count,
                    average_rating = EXCLUDED.average_rating,
                    last_updated = EXCLUDED.last_updated,
                    xp = EXCLUDED.xp,
                    activity_streak = EXCLUDED.activity_streak,
                    last_action_date = EXCLUDED.last_action_date,
                    rank = EXCLUDED.rank,
                    last_active = EXCLUDED.last_active;
                """,
                (
                    stats["user_id"], stats["snft_count"], stats["trade_count"], stats["wallet_count"],
                    stats["comment_count"], stats["reply_count"], stats["share_count"], stats["mention_count"],
                    stats["favorite_count"], stats["star_count"], stats["received_star_count"],
                    stats["average_rating"], stats["last_updated"], stats["xp"], stats["activity_streak"],
                    stats["last_action_date"], stats["rank"], stats["last_active"]
                )
            )
            print(f"Inserted user stats for user {stats['user_id']}")
        except Error as e:
            print(f"Error inserting user stats for user {stats['user_id']}: {e}")
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
            user_stats_data = generate_fake_user_stats(dummy_user_ids)
            insert_fake_user_stats(conn, user_stats_data)
            print("User Stats data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")