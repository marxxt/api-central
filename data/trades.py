import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_trades(user_ids, num_trades_per_user=5):
    """Generates fake trade data."""
    trades = []
    assets = ["MBV", "USDC", "ETH", "BTC"] # Example assets
    trade_types = ["buy", "sell"]

    for user_id in user_ids:
        for _ in range(num_trades_per_user):
            trades.append({
                
                "user_id": user_id,
                "asset": random.choice(assets),
                "type": random.choice(trade_types),
                "amount": round(random.uniform(1, 1000), 2),
                "executed_at": fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc)
            })
    return trades

def insert_fake_trades(conn, trades):
    """Inserts fake trade data."""
    cursor = conn.cursor()
    for trade in trades:
        try:
            cursor.execute(
                """
                INSERT INTO public.trades (id, user_id, asset, type, amount, executed_at, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    asset = EXCLUDED.asset,
                    type = EXCLUDED.type,
                    amount = EXCLUDED.amount,
                    executed_at = EXCLUDED.executed_at,
                    updated_at = now();
                """,
                (trade["id"], trade["user_id"], trade["asset"], trade["type"], trade["amount"], trade["executed_at"])
            )
            print(f"Inserted trade for user {trade['user_id']}")
        except Error as e:
            print(f"Error inserting trade for user {trade['user_id']}: {e}")
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
            # Dummy data for testing trades independently
            dummy_user_ids = [uuid.uuid4() for _ in range(3)]
            trades_data = generate_fake_trades(dummy_user_ids)
            insert_fake_trades(conn, trades_data)
            print("Trades data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")