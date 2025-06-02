import uuid
import random
from datetime import datetime, timezone
from typing import Annotated, List
from pydantic import BaseModel, UUID4, Field, conint
from faker import Faker
from db_utils import supabase_bot  # ✅ Centralized Supabase client

PositiveInt = Annotated[conint(gt=0), Field(description="int value greater than 0")]

fake = Faker()

# --- Pydantic Model ---
class PropertyTokenOwnership(BaseModel):
    id: UUID4
    property_id: UUID4
    wallet_id: UUID4
    tokens_owned: PositiveInt  # Must be >= 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# --- Generator ---
def generate_fake_property_token_ownerships(
    property_ids: List[UUID4], wallet_ids: List[UUID4], num_ownerships_per_property: int = 1
) -> List[PropertyTokenOwnership]:
    ownerships = []

    for prop_id in property_ids:
        for _ in range(num_ownerships_per_property):
            wallet_id = random.choice(wallet_ids)
            ownerships.append(PropertyTokenOwnership(
                id=uuid.uuid4(),
                property_id=prop_id,
                wallet_id=wallet_id,
                tokens_owned=random.randint(1, 10000)
            ))
    return ownerships

# --- Insertor ---
def insert_fake_property_token_ownerships(ownerships: List[PropertyTokenOwnership]):
    for ownership in ownerships:
        try:
            data = ownership.model_dump()
            data["id"] = str(data["id"])
            data["property_id"] = str(data["property_id"])
            data["wallet_id"] = str(data["wallet_id"])
            data["last_updated"] = data["last_updated"].isoformat()

            supabase_bot.table("property_token_ownership").upsert(data).execute()
            print(f"✅ Inserted ownership for property {data['property_id']} by wallet {data['wallet_id']}")
        except Exception as e:
            print(f"❌ Error inserting ownership for property {ownership.property_id} by wallet {ownership.wallet_id}: {e}")

# --- Entry Point ---
if __name__ == "__main__":
    dummy_property_ids = [uuid.uuid4() for _ in range(3)]
    dummy_wallet_ids = [uuid.uuid4() for _ in range(3)]
    ownerships = generate_fake_property_token_ownerships(dummy_property_ids, dummy_wallet_ids)
    insert_fake_property_token_ownerships(ownerships)
    print("🏁 Property Token Ownership data generation and insertion complete.")
