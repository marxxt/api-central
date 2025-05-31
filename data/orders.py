import uuid
import random
from datetime import datetime, timedelta, timezone
from faker import Faker
import psycopg2
from psycopg2 import Error

fake = Faker()

def generate_fake_orders(user_ids, trading_pair_ids, num_orders_per_user=5):
    """Generates fake order data."""
    orders = []
    order_types = ['buy', 'sell']
    trade_types = ['market', 'limit']
    statuses = ['open', 'filled', 'cancelled', 'partial_fill', 'expired']

    for user_id in user_ids:
        for _ in range(num_orders_per_user):
            trading_pair_id = random.choice(trading_pair_ids) if trading_pair_ids else None
            if not trading_pair_id:
                continue

            order_type = random.choice(order_types)
            trade_type = random.choice(trade_types)
            amount = round(random.uniform(1, 1000), 2)
            is_amount_in_base = fake.boolean()
            limit_price = round(random.uniform(0.5, 100), 2) if trade_type == 'limit' else None
            status = random.choice(statuses)
            filled_amount = amount if status == 'filled' else (round(random.uniform(0, amount), 2) if status == 'partial_fill' else 0.0)

            orders.append({
                
                "user_id": user_id,
                "trading_pair_id": trading_pair_id,
                "order_type": order_type,
                "trade_type": trade_type,
                "amount": amount,
                "is_amount_in_base": is_amount_in_base,
                "limit_price": limit_price,
                "status": status,
                "filled_amount": filled_amount,
                "executed_at": fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc)
            })
    return orders

def insert_fake_orders(conn, orders):
    """Inserts fake order data."""
    cursor = conn.cursor()
    for order in orders:
        try:
            cursor.execute(
                """
                INSERT INTO public.orders (
                    id, user_id, trading_pair_id, order_type, trade_type, amount,
                    is_amount_in_base, limit_price, status, filled_amount,
                    executed_at, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    user_id = EXCLUDED.user_id,
                    trading_pair_id = EXCLUDED.trading_pair_id,
                    order_type = EXCLUDED.order_type,
                    trade_type = EXCLUDED.trade_type,
                    amount = EXCLUDED.amount,
                    is_amount_in_base = EXCLUDED.is_amount_in_base,
                    limit_price = EXCLUDED.limit_price,
                    status = EXCLUDED.status,
                    filled_amount = EXCLUDED.filled_amount,
                    executed_at = EXCLUDED.executed_at,
                    updated_at = now();
                """,
                (
                    order["id"], order["user_id"], order["trading_pair_id"], order["order_type"],
                    order["trade_type"], order["amount"], order["is_amount_in_base"],
                    order["limit_price"], order["status"], order["filled_amount"], order["executed_at"]
                )
            )
            print(f"Inserted order {order['id']} for user {order['user_id']}")
        except Error as e:
            print(f"Error inserting order {order['id']} for user {order['user_id']}: {e}")
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
            orders_data = generate_fake_orders(dummy_user_ids, dummy_trading_pair_ids)
            insert_fake_orders(conn, orders_data)
            print("Orders data generation and insertion complete.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")