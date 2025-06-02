import uuid
import random
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel
from faker import Faker
from db_utils import supabase_bot

fake = Faker()

class Order(BaseModel):
    id: str
    user_id: str
    trading_pair_id: str
    order_type: str  # 'buy' or 'sell'
    trade_type: str  # 'market' or 'limit'
    amount: float
    is_amount_in_base: bool
    limit_price: Optional[float]
    status: str
    filled_amount: float
    executed_at: datetime
    created_at: datetime
    updated_at: datetime

def generate_fake_orders(user_ids: List[str], trading_pair_ids: List[str], num_orders_per_user: int = 5) -> List[Order]:
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
            executed_at = fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc)
            timestamp = datetime.now(timezone.utc)

            orders.append(Order(
                id=str(uuid.uuid4()),
                user_id=user_id,
                trading_pair_id=trading_pair_id,
                order_type=order_type,
                trade_type=trade_type,
                amount=amount,
                is_amount_in_base=is_amount_in_base,
                limit_price=limit_price,
                status=status,
                filled_amount=filled_amount,
                executed_at=executed_at,
                created_at=timestamp,
                updated_at=timestamp
            ))
    return orders

def insert_fake_orders(orders: List[Order]) -> None:
    for order in orders:
        try:
            order_data = order.model_dump()
            # Convert datetime objects to ISO 8601 strings
            for key in ['executed_at', 'created_at', 'updated_at']:
                if isinstance(order_data[key], datetime):
                    order_data[key] = order_data[key].isoformat()

            supabase_bot.table("orders").upsert(order_data).execute()
            print(f"✅ Inserted order {order.id} for user {order.user_id}")
        except Exception as e:
            print(f"❌ Error inserting order {order.id} for user {order.user_id}: {e}")

if __name__ == "__main__":
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(3)]
    dummy_trading_pair_ids = ["MBV_USDC", "ETH_USDT"]
    orders_data = generate_fake_orders(dummy_user_ids, dummy_trading_pair_ids)
    insert_fake_orders(orders_data)
    print("🏁 Orders data generation and insertion complete.")
