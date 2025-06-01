import uuid
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_dao_proposals(num_proposals=5):
    """Generates fake DAO proposal data."""
    dao_proposals = []
    for _ in range(num_proposals):
        dao_proposals.append({
            
            "title": fake.sentence(nb_words=6),
            "description": fake.paragraph(nb_sentences=3)
        })
    return dao_proposals

def insert_fake_dao_proposals(conn, dao_proposals):
    """Inserts fake DAO proposal data."""
    cursor = conn.cursor()
    for proposal in dao_proposals:
        try:
            cursor.execute(
                """
                INSERT INTO public.dao_proposals (id, title, description, created_at, updated_at)
                VALUES (%s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    updated_at = now();
                """,
                (proposal["id"], proposal["title"], proposal["description"])
            )
            print(f"Inserted DAO proposal: {proposal['title']}")
        except Error as e:
            print(f"Error inserting DAO proposal {proposal['title']}: {e}")
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
            dao_proposals_data = generate_fake_dao_proposals(num_proposals=3)
            insert_fake_dao_proposals(conn, dao_proposals_data)
            print("DAO Proposals data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")