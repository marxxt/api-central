import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_ip_event_log(num_events=20):
    """Generates fake IP event log data."""
    ip_events = []
    event_types = ['comment', 'mention', 'share', 'login']

    for _ in range(num_events):
        ip_events.append({
            
            "ip_address": fake.ipv4(),
            "event_type": random.choice(event_types),
            "occurred_at": fake.date_time_between(start_date="-1m", end_date="now", tzinfo=timezone.utc)
        })
    return ip_events

def insert_fake_ip_event_log(conn, ip_events):
    """Inserts fake IP event log data."""
    cursor = conn.cursor()
    for event in ip_events:
        try:
            cursor.execute(
                """
                INSERT INTO public.ip_event_log (id, ip_address, event_type, occurred_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    ip_address = EXCLUDED.ip_address,
                    event_type = EXCLUDED.event_type,
                    occurred_at = EXCLUDED.occurred_at;
                """,
                (event["id"], event["ip_address"], event["event_type"], event["occurred_at"])
            )
            print(f"Inserted IP event {event['id']} of type {event['event_type']}")
        except Error as e:
            print(f"Error inserting IP event {event['id']} of type {event['event_type']}: {e}")
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
            ip_event_log_data = generate_fake_ip_event_log()
            insert_fake_ip_event_log(conn, ip_event_log_data)
            print("IP Event Log data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")