import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_transactions(snft_ids, num_transactions_per_snft=3):
    """Generates fake transaction data."""
    transactions = []
    transaction_types = ['BUY', 'SELL', 'TRANSFER', 'EXCHANGE', 'MINT', 'OTHER', 'UNKNOWN']

    for snft_id in snft_ids:
        for _ in range(num_transactions_per_snft):
            transactions.append({
                
                "snft_id": snft_id,
                "type": random.choice(transaction_types),
                "amount": round(random.uniform(1, 10000), 2),
                "timestamp": fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc)
            })
    return transactions

def insert_fake_transactions(conn, transactions):
    """Inserts fake transaction data."""
    cursor = conn.cursor()
    for transaction in transactions:
        try:
            cursor.execute(
                """
                INSERT INTO public.transactions (id, snft_id, type, amount, timestamp, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    snft_id = EXCLUDED.snft_id,
                    type = EXCLUDED.type,
                    amount = EXCLUDED.amount,
                    timestamp = EXCLUDED.timestamp,
                    updated_at = now();
                """,
                (transaction["id"], transaction["snft_id"], transaction["type"], transaction["amount"], transaction["timestamp"])
            )
            print(f"Inserted transaction {transaction['id']} for SNFT {transaction['snft_id']}")
        except Error as e:
            print(f"Error inserting transaction {transaction['id']} for SNFT {transaction['snft_id']}: {e}")
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
            dummy_snft_ids = [uuid.uuid4() for _ in range(3)]
            transactions_data = generate_fake_transactions(dummy_snft_ids)
            insert_fake_transactions(conn, transactions_data)
            print("Transactions data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")