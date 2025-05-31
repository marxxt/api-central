import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_trading_pairs(property_ids, num_pairs_per_property=1):
    """Generates fake trading pair data."""
    trading_pairs = []
    quote_assets = ["USDC", "ETH", "USDT"]

    for prop_id in property_ids:
        for _ in range(num_pairs_per_property):
            base_asset_symbol = fake.unique.lexify(text="???", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            quote_asset_symbol = random.choice(quote_assets)
            pair_id = f"{base_asset_symbol}_{quote_asset_symbol}"

            trading_pairs.append({
                "id": pair_id,
                "base_asset_id": prop_id,
                "base_asset_symbol": base_asset_symbol,
                "quote_asset_symbol": quote_asset_symbol,
                "last_price": round(random.uniform(0.01, 1000), 2),
                "price_change_24h_percent": round(random.uniform(-10, 10), 2),
                "high_24h": round(random.uniform(100, 1200), 2),
                "low_24h": round(random.uniform(0.005, 900), 2),
                "volume_24h_base": round(random.uniform(10000, 1000000), 2),
                "volume_24h_quote": round(random.uniform(5000, 500000), 2),
                "ohlc_history": fake.json(num_rows=5, data_columns=[('open', 'pyfloat'), ('high', 'pyfloat'), ('low', 'pyfloat'), ('close', 'pyfloat')]),
                "volume_history": fake.json(num_rows=5, data_columns=[('volume', 'pyfloat')]),
                "is_favorite": fake.boolean(),
                "order_book_id": fake.uuid4()
            })
    return trading_pairs

def insert_fake_trading_pairs(conn, trading_pairs):
    """Inserts fake trading pair data."""
    cursor = conn.cursor()
    for pair in trading_pairs:
        try:
            cursor.execute(
                """
                INSERT INTO public.trading_pairs (
                    id, base_asset_id, base_asset_symbol, quote_asset_symbol, last_price,
                    price_change_24h_percent, high_24h, low_24h, volume_24h_base,
                    volume_24h_quote, ohlc_history, volume_history, is_favorite,
                    order_book_id, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    base_asset_id = EXCLUDED.base_asset_id,
                    base_asset_symbol = EXCLUDED.base_asset_symbol,
                    quote_asset_symbol = EXCLUDED.quote_asset_symbol,
                    last_price = EXCLUDED.last_price,
                    price_change_24h_percent = EXCLUDED.price_change_24h_percent,
                    high_24h = EXCLUDED.high_24h,
                    low_24h = EXCLUDED.low_24h,
                    volume_24h_base = EXCLUDED.volume_24h_base,
                    volume_24h_quote = EXCLUDED.volume_24h_quote,
                    ohlc_history = EXCLUDED.ohlc_history,
                    volume_history = EXCLUDED.volume_history,
                    is_favorite = EXCLUDED.is_favorite,
                    order_book_id = EXCLUDED.order_book_id,
                    updated_at = now();
                """,
                (
                    pair["id"], pair["base_asset_id"], pair["base_asset_symbol"], pair["quote_asset_symbol"],
                    pair["last_price"], pair["price_change_24h_percent"], pair["high_24h"], pair["low_24h"],
                    pair["volume_24h_base"], pair["volume_24h_quote"], pair["ohlc_history"], pair["volume_history"],
                    pair["is_favorite"], pair["order_book_id"]
                )
            )
            print(f"Inserted trading pair: {pair['id']}")
        except Error as e:
            print(f"Error inserting trading pair {pair['id']}: {e}")
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
            dummy_property_ids = [uuid.uuid4() for _ in range(3)]
            trading_pairs_data = generate_fake_trading_pairs(dummy_property_ids)
            insert_fake_trading_pairs(conn, trading_pairs_data)
            print("Trading pairs data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")