import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_snft_balances(user_ids, snft_ids, num_balances_per_user=2):
    """Generates fake SNFT balances data."""
    snft_balances = []

    for user_id in user_ids:
        # Ensure unique SNFTs per user for balances
        owned_snfts = random.sample(snft_ids, min(num_balances_per_user, len(snft_ids)))
        for snft_id in owned_snfts:
            snft_balances.append({
                
                "user_id": user_id,
                "snft_id": snft_id,
                "token_count": round(random.uniform(1, 1000), 2),
                "avg_buy_price": round(random.uniform(0.1, 100), 2)
            })
    return snft_balances

def insert_fake_snft_balances(conn, snft_balances):
    """Inserts fake SNFT balances data."""
    cursor = conn.cursor()
    for balance in snft_balances:
        try:
            cursor.execute(
                """
                INSERT INTO public.snft_balances (id, user_id, snft_id, token_count, avg_buy_price, updated_at)
                VALUES (%s, %s, %s, %s, %s, now())
                ON CONFLICT (user_id, snft_id) DO UPDATE SET
                    token_count = EXCLUDED.token_count,
                    avg_buy_price = EXCLUDED.avg_buy_price,
                    updated_at = now();
                """,
                (
                    balance["id"], balance["user_id"], balance["snft_id"],
                    balance["token_count"], balance["avg_buy_price"]
                )
            )
            print(f"Inserted SNFT balance for user {balance['user_id']} on SNFT {balance['snft_id']}")
        except Error as e:
            print(f"Error inserting SNFT balance for user {balance['user_id']} on SNFT {balance['snft_id']}: {e}")
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
            dummy_snft_ids = [uuid.uuid4() for _ in range(10)]
            snft_balances_data = generate_fake_snft_balances(dummy_user_ids, dummy_snft_ids)
            insert_fake_snft_balances(conn, snft_balances_data)
            print("SNFT Balances data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")