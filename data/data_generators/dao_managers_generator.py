import uuid
import random
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_dao_managers(dao_ids, user_ids, num_managers_per_dao=2):
    """Generates fake DAO manager data."""
    dao_managers = []
    for dao_id in dao_ids:
        # Ensure unique managers per DAO
        managers = random.sample(user_ids, min(num_managers_per_dao, len(user_ids)))
        for user_id in managers:
            dao_managers.append({
                "dao_id": dao_id,
                "user_id": user_id
            })
    return dao_managers

def insert_fake_dao_managers(conn, dao_managers):
    """Inserts fake DAO manager data."""
    cursor = conn.cursor()
    for manager in dao_managers:
        try:
            cursor.execute(
                """
                INSERT INTO public.dao_managers (dao_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (dao_id, user_id) DO NOTHING;
                """,
                (manager["dao_id"], manager["user_id"])
            )
            print(f"Inserted DAO manager: DAO {manager['dao_id']}, User {manager['user_id']}")
        except Error as e:
            print(f"Error inserting DAO manager DAO {manager['dao_id']}, User {manager['user_id']}: {e}")
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
            dao_managers_data = generate_fake_dao_managers(dummy_dao_ids, dummy_user_ids)
            insert_fake_dao_managers(conn, dao_managers_data)
            print("DAO Managers data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")