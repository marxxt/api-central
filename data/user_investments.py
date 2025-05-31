import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_user_investments(user_ids, property_asset_ids, num_investments_per_user=2):
    """Generates fake user investment data."""
    user_investments = []
    statuses = ['Owned', 'Staked', 'ListedForSale', 'InBot']
    currencies = ["USDC", "ETH", "BTC"]

    for user_id in user_ids:
        for _ in range(num_investments_per_user):
            property_asset_id = random.choice(property_asset_ids) if property_asset_ids else None
            if not property_asset_id:
                continue

            user_investments.append({
                
                "user_id": user_id,
                "property_asset_id": property_asset_id,
                "tokens_owned": round(random.uniform(1, 1000), 2),
                "avg_buy_price_per_token": round(random.uniform(0.1, 100), 2),
                "avg_buy_price_currency": random.choice(currencies),
                "purchase_date": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc),
                "status": random.choice(statuses)
            })
    return user_investments

def insert_fake_user_investments(conn, user_investments):
    """Inserts fake user investment data."""
    cursor = conn.cursor()
    for investment in user_investments:
        try:
            cursor.execute(
                """
                INSERT INTO public.user_investments (
                    id, user_id, property_asset_id, tokens_owned, avg_buy_price_per_token,
                    avg_buy_price_currency, purchase_date, status, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    property_asset_id = EXCLUDED.property_asset_id,
                    tokens_owned = EXCLUDED.tokens_owned,
                    avg_buy_price_per_token = EXCLUDED.avg_buy_price_per_token,
                    avg_buy_price_currency = EXCLUDED.avg_buy_price_currency,
                    purchase_date = EXCLUDED.purchase_date,
                    status = EXCLUDED.status,
                    updated_at = now();
                """,
                (
                    investment["id"], investment["user_id"], investment["property_asset_id"],
                    investment["tokens_owned"], investment["avg_buy_price_per_token"],
                    investment["avg_buy_price_currency"], investment["purchase_date"],
                    investment["status"]
                )
            )
            print(f"Inserted user investment {investment['id']} for user {investment['user_id']}")
        except Error as e:
            print(f"Error inserting user investment {investment['id']} for user {investment['user_id']}: {e}")
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
            dummy_user_ids = [uuid.uuid4() for _ in range(3)]
            dummy_property_asset_ids = [uuid.uuid4() for _ in range(3)]
            user_investments_data = generate_fake_user_investments(dummy_user_ids, dummy_property_asset_ids)
            insert_fake_user_investments(conn, user_investments_data)
            print("User Investments data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")