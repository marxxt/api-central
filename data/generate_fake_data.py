import os
import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Faker
fake = Faker()

# Database connection details
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establishes and returns a database connection."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set.")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def generate_fake_users(num_users=10):
    """Generates fake user data for auth.users table."""
    users = []
    for _ in range(num_users):
        user_id = uuid.uuid4()
        email = fake.unique.email()
        password = fake.password()
        username = fake.unique.user_name()
        full_name = fake.name()
        avatar_url = fake.image_url()
        # Supabase auth.users table has more fields, but these are sufficient for FKs
        users.append({
            "id": user_id,
            "email": email,
            "raw_user_meta_data": {"username": username, "full_name": full_name, "avatar_url": avatar_url}
        })
    return users

def insert_fake_users(conn, users):
    """Inserts fake user data into auth.users table."""
    cursor = conn.cursor()
    for user in users:
        try:
            # Note: Directly inserting into auth.users is generally not recommended
            # as Supabase manages this table. This is for demonstration purposes.
            # In a real app, users would register via Supabase Auth.
            cursor.execute(
                """
                INSERT INTO auth.users (id, email, encrypted_password, raw_user_meta_data, created_at, updated_at)
                VALUES (%s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    email = EXCLUDED.email,
                    raw_user_meta_data = EXCLUDED.raw_user_meta_data,
                    updated_at = now();
                """,
                (user["id"], user["email"], fake.password(), user["raw_user_meta_data"])
            )
            print(f"Inserted user: {user['email']}")
        except Error as e:
            print(f"Error inserting user {user['email']}: {e}")
            conn.rollback()
    conn.commit()
    cursor.close()

def generate_fake_wallets(user_ids, num_wallets_per_user=2):
    """Generates fake wallet data."""
    wallets = []
    for user_id in user_ids:
        for _ in range(num_wallets_per_user):
            wallets.append({
                
                "user_id": user_id,
                "address": fake.sha256(),
                "balance": round(random.uniform(100, 100000), 2),
                "currency": random.choice(["USD", "ETH", "BTC", "USDC"])
            })
    return wallets

def insert_fake_wallets(conn, wallets):
    """Inserts fake wallet data."""
    cursor = conn.cursor()
    for wallet in wallets:
        try:
            cursor.execute(
                """
                INSERT INTO public.wallets (id, user_id, address, balance, currency, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    address = EXCLUDED.address,
                    balance = EXCLUDED.balance,
                    currency = EXCLUDED.currency,
                    updated_at = now();
                """,
                (wallet["id"], wallet["user_id"], wallet["address"], wallet["balance"], wallet["currency"])
            )
            print(f"Inserted wallet for user {wallet['user_id']}")
        except Error as e:
            print(f"Error inserting wallet for user {wallet['user_id']}: {e}")
            conn.rollback()
    conn.commit()
    cursor.close()

def generate_fake_collections(user_ids, num_collections_per_user=1):
    """Generates fake collection data."""
    collections = []
    for user_id in user_ids:
        for _ in range(num_collections_per_user):
            collections.append({
                
                "user_id": user_id,
                "name": fake.word().capitalize() + " Collection",
                "color": fake.hex_color(),
                "count": random.randint(1, 50)
            })
    return collections

def insert_fake_collections(conn, collections):
    """Inserts fake collection data."""
    cursor = conn.cursor()
    for collection in collections:
        try:
            cursor.execute(
                """
                INSERT INTO public.collections (id, user_id, name, color, count, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    name = EXCLUDED.name,
                    color = EXCLUDED.color,
                    count = EXCLUDED.count,
                    updated_at = now();
                """,
                (collection["id"], collection["user_id"], collection["name"], collection["color"], collection["count"])
            )
            print(f"Inserted collection: {collection['name']}")
        except Error as e:
            print(f"Error inserting collection {collection['name']}: {e}")
            conn.rollback()
    conn.commit()
    cursor.close()

def generate_fake_properties(user_ids, num_properties_per_user=3):
    """Generates fake property data."""
    properties = []
    property_types = ['SFR', 'MultiFamily', 'Commercial']
    statuses = ['For Sale', 'Rented', 'Pending']
    for user_id in user_ids:
        for _ in range(num_properties_per_user):
            properties.append({
                
                "user_id": user_id,
                "name": fake.street_name() + " Property",
                "token_symbol": fake.unique.lexify(text="???", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                "description": fake.paragraph(),
                "image_url": fake.image_url(),
                "address": fake.address(),
                "property_type": random.choice(property_types),
                "status": random.choice(statuses),
                "valuation": round(random.uniform(100000, 5000000), 2),
                "total_tokens": random.randint(1000, 100000),
                "apy": round(random.uniform(0.03, 0.15), 4),
                "date_listed": fake.date_time_between(start_date="-2y", end_date="now", tzinfo=timezone.utc)
            })
    return properties

def insert_fake_properties(conn, properties):
    """Inserts fake property data."""
    cursor = conn.cursor()
    for prop in properties:
        try:
            cursor.execute(
                """
                INSERT INTO public.properties (id, user_id, name, token_symbol, description, image_url, address, property_type, status, valuation, total_tokens, apy, date_listed, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    name = EXCLUDED.name,
                    token_symbol = EXCLUDED.token_symbol,
                    description = EXCLUDED.description,
                    image_url = EXCLUDED.image_url,
                    address = EXCLUDED.address,
                    property_type = EXCLUDED.property_type,
                    status = EXCLUDED.status,
                    valuation = EXCLUDED.valuation,
                    total_tokens = EXCLUDED.total_tokens,
                    apy = EXCLUDED.apy,
                    date_listed = EXCLUDED.date_listed,
                    updated_at = now();
                """,
                (prop["id"], prop["user_id"], prop["name"], prop["token_symbol"], prop["description"], prop["image_url"], prop["address"], prop["property_type"], prop["status"], prop["valuation"], prop["total_tokens"], prop["apy"], prop["date_listed"])
            )
            print(f"Inserted property: {prop['name']}")
        except Error as e:
            print(f"Error inserting property {prop['name']}: {e}")
            conn.rollback()
    conn.commit()
    cursor.close()

def generate_fake_daos(num_daos=5):
    """Generates fake DAO data."""
    daos = []
    dao_types = ['single_property', 'multi_property', 'contractor', 'hedge_fund', 'realtor_team', 'reit', 'developer', 'community', 'guild', 'foundation', 'investor_club']
    scopes = ['local', 'regional', 'national', 'global']
    for _ in range(num_daos):
        daos.append({
            
            "name": fake.company() + " DAO",
            "link": fake.url(),
            "description": fake.paragraph(),
            "snft_id": None, # Can be updated later if needed, as it's nullable
            "dao_type": random.choice(dao_types),
            "operational_scope": random.choice(scopes),
            "valuation": round(random.uniform(1000000, 100000000), 2),
            "currency": "USD",
            "total_token_supply": random.randint(1000000, 1000000000),
            "treasury_address": fake.sha256(),
            "voting_token_address": fake.sha256(),
            "governance_model": random.choice(["1-token-1-vote", "quadratic", "liquid"])
        })
    return daos

def insert_fake_daos(conn, daos):
    """Inserts fake DAO data."""
    cursor = conn.cursor()
    for dao in daos:
        try:
            cursor.execute(
                """
                INSERT INTO public.daos (id, name, link, description, snft_id, dao_type, operational_scope, valuation, currency, total_token_supply, treasury_address, voting_token_address, governance_model, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    link = EXCLUDED.link,
                    description = EXCLUDED.description,
                    snft_id = EXCLUDED.snft_id,
                    dao_type = EXCLUDED.dao_type,
                    operational_scope = EXCLUDED.operational_scope,
                    valuation = EXCLUDED.valuation,
                    currency = EXCLUDED.currency,
                    total_token_supply = EXCLUDED.total_token_supply,
                    treasury_address = EXCLUDED.treasury_address,
                    voting_token_address = EXCLUDED.voting_token_address,
                    governance_model = EXCLUDED.governance_model,
                    updated_at = now();
                """,
                (dao["id"], dao["name"], dao["link"], dao["description"], dao["snft_id"], dao["dao_type"], dao["operational_scope"], dao["valuation"], dao["currency"], dao["total_token_supply"], dao["treasury_address"], dao["voting_token_address"], dao["governance_model"])
            )
            print(f"Inserted DAO: {dao['name']}")
        except Error as e:
            print(f"Error inserting DAO {dao['name']}: {e}")
            conn.rollback()
    conn.commit()
    cursor.close()

def main():
    conn = None
    try:
        conn = get_db_connection()
        if conn:
            # Generate and insert users
            print("\n--- Generating Users ---")
            users = generate_fake_users(num_users=5)
            user_ids = [user["id"] for user in users]
            insert_fake_users(conn, users)

            # Generate and insert wallets
            print("\n--- Generating Wallets ---")
            wallets = generate_fake_wallets(user_ids)
            insert_fake_wallets(conn, wallets)

            # Generate and insert collections
            print("\n--- Generating Collections ---")
            collections = generate_fake_collections(user_ids)
            insert_fake_collections(conn, collections)

            # Generate and insert properties
            print("\n--- Generating Properties ---")
            properties = generate_fake_properties(user_ids)
            insert_fake_properties(conn, properties)

            # Generate and insert DAOs
            print("\n--- Generating DAOs ---")
            daos = generate_fake_daos()
            insert_fake_daos(conn, daos)

            print("\nFake data generation for core tables completed.")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()