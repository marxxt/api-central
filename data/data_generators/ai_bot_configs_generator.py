import uuid
import random
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_ai_bot_configs(user_ids, trading_pair_ids, num_configs_per_user=1):
    """Generates fake AI bot configuration data."""
    ai_bot_configs = []
    strategies = ['Grid', 'DCA', 'ML_Trend', 'Arbitrage']
    risk_levels = ['Low', 'Medium', 'High']
    quote_assets = ["USDC", "ETH", "USDT"]

    for user_id in user_ids:
        for _ in range(num_configs_per_user):
            trading_pair_id = random.choice(trading_pair_ids) if trading_pair_ids else None
            if not trading_pair_id:
                continue # Skip if no trading pairs are available

            ai_bot_configs.append({
                
                "user_id": user_id,
                "trading_pair_id": trading_pair_id,
                "strategy": random.choice(strategies),
                "investment_amount": round(random.uniform(100, 10000), 2),
                "quote_asset_for_investment": random.choice(quote_assets),
                "risk_level": random.choice(risk_levels),
                "is_active": fake.boolean(),
                "config_params": fake.json(num_rows=1, data_columns=[('param1', 'pyint'), ('param2', 'pybool')])
            })
    return ai_bot_configs

def insert_fake_ai_bot_configs(conn, ai_bot_configs):
    """Inserts fake AI bot configuration data."""
    cursor = conn.cursor()
    for config in ai_bot_configs:
        try:
            cursor.execute(
                """
                INSERT INTO public.ai_bot_configs (
                    id, user_id, trading_pair_id, strategy, investment_amount,
                    quote_asset_for_investment, risk_level, is_active, config_params,
                    created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    trading_pair_id = EXCLUDED.trading_pair_id,
                    strategy = EXCLUDED.strategy,
                    investment_amount = EXCLUDED.investment_amount,
                    quote_asset_for_investment = EXCLUDED.quote_asset_for_investment,
                    risk_level = EXCLUDED.risk_level,
                    is_active = EXCLUDED.is_active,
                    config_params = EXCLUDED.config_params,
                    updated_at = now();
                """,
                (
                    config["id"], config["user_id"], config["trading_pair_id"], config["strategy"],
                    config["investment_amount"], config["quote_asset_for_investment"],
                    config["risk_level"], config["is_active"], config["config_params"]
                )
            )
            print(f"Inserted AI Bot Config for user {config['user_id']} on pair {config['trading_pair_id']}")
        except Error as e:
            print(f"Error inserting AI Bot Config for user {config['user_id']} on pair {config['trading_pair_id']}: {e}")
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
            dummy_user_ids = [uuid.uuid4() for _ in range(3)]
            dummy_trading_pair_ids = ["MBV_USDC", "ETH_USDT"]
            ai_bot_configs_data = generate_fake_ai_bot_configs(dummy_user_ids, dummy_trading_pair_ids)
            insert_fake_ai_bot_configs(conn, ai_bot_configs_data)
            print("AI Bot Configs data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")