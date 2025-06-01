import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_dao_voting_epochs(dao_ids, proposal_ids, num_epochs_per_dao=3):
    """Generates fake DAO voting epoch data."""
    dao_voting_epochs = []

    for dao_id in dao_ids:
        for i in range(num_epochs_per_dao):
            start_time = fake.date_time_between(start_date=f"-{i+1}y", end_date=f"-{i}y", tzinfo=timezone.utc)
            end_time = start_time + timedelta(days=random.randint(7, 30))
            winning_proposal_id = random.choice(proposal_ids) if proposal_ids and random.random() > 0.3 else None # Optional winning proposal

            dao_voting_epochs.append({
                
                "dao_id": dao_id,
                "epoch_number": i + 1,
                "start_time": start_time,
                "end_time": end_time,
                "total_votes_cast": random.randint(10, 1000),
                "winning_proposal_id": winning_proposal_id
            })
    return dao_voting_epochs

def insert_fake_dao_voting_epochs(conn, dao_voting_epochs):
    """Inserts fake DAO voting epoch data."""
    cursor = conn.cursor()
    for epoch in dao_voting_epochs:
        try:
            cursor.execute(
                """
                INSERT INTO public.dao_voting_epochs (
                    id, dao_id, epoch_number, start_time, end_time,
                    total_votes_cast, winning_proposal_id, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, now())
                ON CONFLICT (dao_id, epoch_number) DO UPDATE SET
                    start_time = EXCLUDED.start_time,
                    end_time = EXCLUDED.end_time,
                    total_votes_cast = EXCLUDED.total_votes_cast,
                    winning_proposal_id = EXCLUDED.winning_proposal_id;
                """,
                (
                    epoch["id"], epoch["dao_id"], epoch["epoch_number"],
                    epoch["start_time"], epoch["end_time"], epoch["total_votes_cast"],
                    epoch["winning_proposal_id"]
                )
            )
            print(f"Inserted DAO voting epoch {epoch['epoch_number']} for DAO {epoch['dao_id']}")
        except Error as e:
            print(f"Error inserting DAO voting epoch {epoch['epoch_number']} for DAO {epoch['dao_id']}: {e}")
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
            dummy_proposal_ids = [uuid.uuid4() for _ in range(5)]
            dao_voting_epochs_data = generate_fake_dao_voting_epochs(dummy_dao_ids, dummy_proposal_ids)
            insert_fake_dao_voting_epochs(conn, dao_voting_epochs_data)
            print("DAO Voting Epochs data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")