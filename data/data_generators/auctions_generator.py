import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_auctions(property_ids, seller_ids, num_auctions_per_property=1):
    """Generates fake auction data."""
    auctions = []
    auction_types = ["Whole Project", "Individual Tokens"]
    statuses = ["active", "pending", "closed", "completed"]

    for prop_id in property_ids:
        for _ in range(num_auctions_per_property):
            seller_id = random.choice(seller_ids) if seller_ids else None
            start_time = fake.date_time_between(start_date="-1m", end_date="now", tzinfo=timezone.utc)
            end_time = start_time + timedelta(days=random.randint(1, 30))

            auctions.append({
                
                "property_id": prop_id,
                "seller_id": seller_id,
                "type": random.choice(auction_types),
                "status": random.choice(statuses),
                "start_time": start_time,
                "end_time": end_time,
                "starting_price": round(random.uniform(1000, 1000000), 2)
            })
    return auctions

def insert_fake_auctions(conn, auctions):
    """Inserts fake auction data."""
    cursor = conn.cursor()
    for auction in auctions:
        try:
            cursor.execute(
                """
                INSERT INTO public.auctions (id, property_id, seller_id, type, status, start_time, end_time, starting_price, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    property_id = EXCLUDED.property_id,
                    seller_id = EXCLUDED.seller_id,
                    type = EXCLUDED.type,
                    status = EXCLUDED.status,
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time,
                    starting_price = EXCLUDED.starting_price,
                    updated_at = now();
                """,
                (auction["id"], auction["property_id"], auction["seller_id"], auction["type"], auction["status"], auction["start_time"], auction["end_time"], auction["starting_price"])
            )
            print(f"Inserted auction for property {auction['property_id']}")
        except Error as e:
            print(f"Error inserting auction for property {auction['property_id']}: {e}")
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
            # Dummy data for testing auctions independently
            dummy_property_ids = [uuid.uuid4() for _ in range(3)]
            dummy_seller_ids = [uuid.uuid4() for _ in range(3)]
            auctions_data = generate_fake_auctions(dummy_property_ids, dummy_seller_ids)
            insert_fake_auctions(conn, auctions_data)
            print("Auctions data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")