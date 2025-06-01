import uuid
import random
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_dao_contractors(dao_ids, contractor_ids, num_contractors_per_dao=3):
    """Generates fake DAO contractor data."""
    dao_contractors = []
    for dao_id in dao_ids:
        # Ensure unique contractors per DAO
        contractors = random.sample(contractor_ids, min(num_contractors_per_dao, len(contractor_ids)))
        for contractor_id in contractors:
            dao_contractors.append({
                "dao_id": dao_id,
                "contractor_id": contractor_id
            })
    return dao_contractors

def insert_fake_dao_contractors(conn, dao_contractors):
    """Inserts fake DAO contractor data."""
    cursor = conn.cursor()
    for dc in dao_contractors:
        try:
            cursor.execute(
                """
                INSERT INTO public.dao_contractors (dao_id, contractor_id)
                VALUES (%s, %s)
                ON CONFLICT (dao_id, contractor_id) DO NOTHING;
                """,
                (dc["dao_id"], dc["contractor_id"])
            )
            print(f"Inserted DAO contractor: DAO {dc['dao_id']}, Contractor {dc['contractor_id']}")
        except Error as e:
            print(f"Error inserting DAO contractor DAO {dc['dao_id']}, Contractor {dc['contractor_id']}: {e}")
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
            dummy_contractor_ids = [uuid.uuid4() for _ in range(10)]
            dao_contractors_data = generate_fake_dao_contractors(dummy_dao_ids, dummy_contractor_ids)
            insert_fake_dao_contractors(conn, dao_contractors_data)
            print("DAO Contractors data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")