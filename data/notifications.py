import uuid
import random
from datetime import datetime, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_notifications(recipient_ids, num_notifications_per_recipient=5):
    """Generates fake notification data."""
    notifications = []
    notification_types = ['mention', 'xp', 'badge', 'follow', 'snft_status']

    for recipient_id in recipient_ids:
        for _ in range(num_notifications_per_recipient):
            notifications.append({
                
                "recipient_id": recipient_id,
                "type": random.choice(notification_types),
                "metadata": fake.json(num_rows=1, data_columns=[('key', 'word'), ('value', 'sentence')]),
                "is_read": fake.boolean(chance_of_getting_true=70),
                "created_at": fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)
            })
    return notifications

def insert_fake_notifications(conn, notifications):
    """Inserts fake notification data."""
    cursor = conn.cursor()
    for notification in notifications:
        try:
            cursor.execute(
                """
                INSERT INTO public.notifications (id, recipient_id, type, metadata, is_read, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    recipient_id = EXCLUDED.recipient_id,
                    type = EXCLUDED.type,
                    metadata = EXCLUDED.metadata,
                    is_read = EXCLUDED.is_read,
                    created_at = EXCLUDED.created_at;
                """,
                (
                    notification["id"], notification["recipient_id"], notification["type"],
                    notification["metadata"], notification["is_read"], notification["created_at"]
                )
            )
            print(f"Inserted notification {notification['id']} for recipient {notification['recipient_id']}")
        except Error as e:
            print(f"Error inserting notification {notification['id']} for recipient {notification['recipient_id']}: {e}")
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
            dummy_recipient_ids = [uuid.uuid4() for _ in range(5)]
            notifications_data = generate_fake_notifications(dummy_recipient_ids)
            insert_fake_notifications(conn, notifications_data)
            print("Notifications data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")