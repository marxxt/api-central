from typing import Annotated, List, Literal, cast
from pydantic import BaseModel, Field, constr, condecimal
from faker import Faker
from decimal import Decimal
import random
import uuid
from datetime import datetime, timezone
from db_utils import supabase_bot  # ✅ Use centralized config

MinLength = Annotated[constr(min_length=1), Field(description="min length 1")]
PositiveDecimal = Annotated[condecimal(gt=0), Field(description="Decimal value greater than 0")]

fake = Faker()


class TradeModel(BaseModel):
    user_id: str
    asset: MinLength
    type: Literal["buy", "sell"]  # ✅ Clean enum-like validation
    amount: PositiveDecimal
    executed_at: datetime


def generate_fake_trades(user_ids: List[str], assets, num_trades_per_user: int = 5) -> List[TradeModel]:
    print(user_ids[0], assets[0])
    trade_types = ["buy", "sell"]
    trades = []
    for user_id in user_ids:
        for _ in range(num_trades_per_user):
            trade = TradeModel(
                user_id=user_id,
                asset=(random.choice(assets))[1],
                type=cast(Literal["buy", "sell"], random.choice(trade_types)),
                amount=round(Decimal(random.uniform(1, 1000)), 2),
                executed_at=fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc)
            )
            trades.append(trade)
    return trades


def insert_fake_trades(trades: List[TradeModel]) -> List[str]:
    inserted_ids = []
    for trade in trades:
        try:
            trade_data = trade.model_dump() 
            trade_data["amount"] = str(trade_data["amount"])  # 🧮 Decimal to str
            trade_data["executed_at"] = trade_data["executed_at"].isoformat() # Convert datetime to ISO format string
            response = supabase_bot.table("trades").upsert(trade_data).execute()
            inserted_id = response.data[0]["id"]
            print(f"✅ Inserted trade for user {trade.user_id}: {inserted_id}")
            inserted_ids.append(inserted_id)
        except Exception as e:
            print(f"❌ Error inserting trade for user {trade.user_id}: {e}")
    return inserted_ids


if __name__ == "__main__":
    pass
