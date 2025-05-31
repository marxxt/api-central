import uuid
import random
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_dao_members(dao_ids, user_ids, num_members_per_dao=5):
    """Generates fake DAO member data."""
    dao_members = []
    for dao_id in dao_ids:
        # Ensure unique members per DAO
        members = random.sample(user_ids, min(num_members_per_dao, len(user_ids)))
        for user_id in members:
            dao_members.append({
                "dao_id": dao_id,
                "user_id": user_id
            })
    return dao_members

def insert_fake_dao_members(conn, dao_members):
    """Inserts fake DAO member data."""
    cursor = conn.cursor()
    for member in dao_members:
        try:
            cursor.execute(
                """
                INSERT INTO public.dao_members (dao_id, user_id)
                VALUES (%s, %s)
                ON CONFLICT (dao_id, user_id) DO NOTHING;
                """,
                (member["dao_id"], member["user_id"])
            )
            print(f"Inserted DAO member: DAO {member['dao_id']}, User {member['user_id']}")
        except Error as e:
            print(f"Error inserting DAO member DAO {member['dao_id']}, User {member['user_id']}: {e}")
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
            dao_members_data = generate_fake_dao_members(dummy_dao_ids, dummy_user_ids)
            insert_fake_dao_members(conn, dao_members_data)
            print("DAO Members data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")