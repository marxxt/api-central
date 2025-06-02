import uuid
import random
from decimal import Decimal
from typing import Annotated, List, Literal, cast
from faker import Faker
from pydantic import BaseModel, Field, UUID4, condecimal, constr
from db_utils import supabase_bot  # ✅ centralized Supabase client

Min2Char = Annotated[constr(min_length=2), Field(description="min 2 characters")]
Min3Char = Annotated[constr(min_length=3), Field(description="min 3 characters")]
PositiveDecimal = Annotated[condecimal(gt=0), Field(description="Decimal value greater than 0")]

fake = Faker()

# 📘 Pydantic model
class AIBotConfigModel(BaseModel):
    user_id: str
    trading_pair_id: str
    strategy: Min2Char
    investment_amount: PositiveDecimal
    quote_asset_for_investment: Min3Char
    risk_level: Literal["Low", "Medium", "High"]
    is_active: bool
    config_params: dict

# 🔧 Generator
def generate_fake_ai_bot_configs(user_ids: List[str], trading_pair_ids: List[str], num_configs_per_user: int = 1) -> List[AIBotConfigModel]:
    strategies = ['Grid', 'DCA', 'ML_Trend', 'Arbitrage']
    risk_levels = ['Low', 'Medium', 'High']
    quote_assets = ["USDC", "ETH", "USDT"]

    configs = []
    for user_id in user_ids:
        for _ in range(num_configs_per_user):
            trading_pair_id = random.choice(trading_pair_ids) if trading_pair_ids else None
            if not trading_pair_id:
                continue
            
            config = AIBotConfigModel(
                user_id=user_id,
                trading_pair_id=trading_pair_id,
                strategy=random.choice(strategies),
                investment_amount=Decimal(str(round(random.uniform(100, 10000), 2))),
                quote_asset_for_investment=random.choice(quote_assets),
                risk_level=cast(Literal['Low', 'Medium', 'High'], random.choice(risk_levels)),
                is_active=fake.boolean(),
                config_params=fake.pydict(nb_elements=2, value_types=[int, bool])
            )
            configs.append(config)
    return configs

# 🚀 Insert
def insert_fake_ai_bot_configs(configs: List[AIBotConfigModel]) -> List[str]:
    inserted_ids = []
    for config in configs:
        try:
            data = config.model_dump()
            data["investment_amount"] = str(data["investment_amount"])  # ensure Decimal serializable
            response = supabase_bot.table("ai_bot_configs").upsert(data).execute()
            inserted_id = response.data[0]["id"]
            print(f"✅ Inserted AI Bot Config for user {config.user_id} on pair {config.trading_pair_id}")
            inserted_ids.append(inserted_id)
        except Exception as e:
            print(f"❌ Error inserting config for user {config.user_id} on pair {config.trading_pair_id}: {e}")
    return inserted_ids

# 🔁 Main
if __name__ == "__main__":
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(3)]
    dummy_trading_pair_ids = ["MBV_USDC", "ETH_USDT"]
    ai_bot_configs_data = generate_fake_ai_bot_configs(dummy_user_ids, dummy_trading_pair_ids)
    insert_fake_ai_bot_configs(ai_bot_configs_data)
    print("🏁 AI Bot Configs data generation and insertion complete.")
