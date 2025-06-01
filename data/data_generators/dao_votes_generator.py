import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_dao_votes(proposal_ids, user_ids, num_votes_per_proposal=5):
    """Generates fake DAO vote data."""
    dao_votes = []
    votes = ['yes', 'no', 'abstain']

    for proposal_id in proposal_ids:
        # Ensure unique user votes per proposal
        voters = random.sample(user_ids, min(num_votes_per_proposal, len(user_ids)))
        for user_id in voters:
            dao_votes.append({
                
                "proposal_id": proposal_id,
                "user_id": user_id,
                "vote": random.choice(votes),
                "voted_at": fake.date_time_between(start_date="-1m", end_date="now", tzinfo=timezone.utc)
            })
    return dao_votes

def insert_fake_dao_votes(conn, dao_votes):
    """Inserts fake DAO vote data."""
    cursor = conn.cursor()
    for vote in dao_votes:
        try:
            cursor.execute(
                """
                INSERT INTO public.dao_votes (id, proposal_id, user_id, vote, voted_at, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (proposal_id, user_id) DO UPDATE SET
                    vote = EXCLUDED.vote,
                    voted_at = EXCLUDED.voted_at,
                    updated_at = now();
                """,
                (vote["id"], vote["proposal_id"], vote["user_id"], vote["vote"], vote["voted_at"])
            )
            print(f"Inserted DAO vote for proposal {vote['proposal_id']} by user {vote['user_id']}")
        except Error as e:
            print(f"Error inserting DAO vote for proposal {vote['proposal_id']} by user {vote['user_id']}: {e}")
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
            dummy_proposal_ids = [uuid.uuid4() for _ in range(3)]
            dummy_user_ids = [uuid.uuid4() for _ in range(5)]
            dao_votes_data = generate_fake_dao_votes(dummy_proposal_ids, dummy_user_ids)
            insert_fake_dao_votes(conn, dao_votes_data)
            print("DAO Votes data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")