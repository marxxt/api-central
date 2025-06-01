import uuid
import random
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_contractors(dao_ids, num_contractors=10):
    """Generates fake contractor data."""
    contractors = []
    contractor_types = [
        'builder', 'architect', 'plumber', 'electrician', 'landscaper',
        'general_contractor', 'interior_designer', 'inspector', 'lawyer',
        'engineer', 'broker', 'developer', 'accountant', 'property_manager', 'other'
    ]

    for _ in range(num_contractors):
        dao_id = random.choice(dao_ids) if dao_ids else None
        contractor_type = random.choice(contractor_types)
        
        contractors.append({
            
            "dao_id": dao_id,
            "company": fake.company(),
            "contact": fake.name(),
            "link": fake.url(),
            "type": contractor_type,
            "other_type": fake.word() if contractor_type == 'other' else None
        })
    return contractors

def insert_fake_contractors(conn, contractors):
    """Inserts fake contractor data."""
    cursor = conn.cursor()
    for contractor in contractors:
        try:
            cursor.execute(
                """
                INSERT INTO public.contractors (id, dao_id, company, contact, link, type, other_type, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    dao_id = EXCLUDED.dao_id,
                    company = EXCLUDED.company,
                    contact = EXCLUDED.contact,
                    link = EXCLUDED.link,
                    type = EXCLUDED.type,
                    other_type = EXCLUDED.other_type,
                    updated_at = now();
                """,
                (
                    contractor["id"], contractor["dao_id"], contractor["company"],
                    contractor["contact"], contractor["link"], contractor["type"],
                    contractor["other_type"]
                )
            )
            print(f"Inserted contractor: {contractor['company']}")
        except Error as e:
            print(f"Error inserting contractor {contractor['company']}: {e}")
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
            contractors_data = generate_fake_contractors(dummy_dao_ids)
            insert_fake_contractors(conn, contractors_data)
            print("Contractors data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")