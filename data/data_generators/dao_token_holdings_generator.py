import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_dao_token_holdings(dao_ids, user_ids, num_holdings_per_dao=5):
    """Generates fake DAO token holdings data."""
    dao_token_holdings = []
    for dao_id in dao_ids:
        # Ensure unique users per DAO for holdings
        holders = random.sample(user_ids, min(num_holdings_per_dao, len(user_ids)))
        for user_id in holders:
            dao_token_holdings.append({
                
                "dao_id": dao_id,
                "user_id": user_id,
                "token_amount": round(random.uniform(100, 100000), 2),
                "valuation_at_entry": round(random.uniform(0.1, 100), 2),
                "property_invested_ids": [uuid.uuid4() for _ in range(random.randint(0, 3))] # Dummy property IDs
            })
    return dao_token_holdings

def insert_fake_dao_token_holdings(conn, dao_token_holdings):
    """Inserts fake DAO token holdings data."""
    cursor = conn.cursor()
    for holding in dao_token_holdings:
        try:
            cursor.execute(
                """
                INSERT INTO public.dao_token_holdings (id, dao_id, user_id, token_amount, valuation_at_entry, property_invested_ids, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (id) DO UPDATE SET
                    dao_id = EXCLUDED.dao_id,
                    user_id = EXCLUDED.user_id,
                    token_amount = EXCLUDED.token_amount,
                    valuation_at_entry = EXCLUDED.valuation_at_entry,
                    property_invested_ids = EXCLUDED.property_invested_ids;
                """,
                (
                    holding["id"], holding["dao_id"], holding["user_id"],
                    holding["token_amount"], holding["valuation_at_entry"],
                    holding["property_invested_ids"]
                )
            )
            print(f"Inserted DAO token holding for DAO {holding['dao_id']} by user {holding['user_id']}")
        except Error as e:
            print(f"Error inserting DAO token holding for DAO {holding['dao_id']} by user {holding['user_id']}: {e}")
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
            dummy_dao_ids = [uuid.uuid4() for _ in range(3)]
            dummy_user_ids = [uuid.uuid4() for _ in range(10)]
            dao_token_holdings_data = generate_fake_dao_token_holdings(dummy_dao_ids, dummy_user_ids)
            insert_fake_dao_token_holdings(conn, dao_token_holdings_data)
            print("DAO Token Holdings data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")