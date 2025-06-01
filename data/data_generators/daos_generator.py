from decimal import Decimal
import uuid
import random
from typing import Annotated, List
from pydantic import BaseModel, Field, HttpUrl, constr, condecimal, conint
from faker import Faker
from db_utils import supabase_bot

UppercaseChar = Annotated[constr(to_upper=True), Field(description="Uppercase characters")]
PositiveDecimal = Annotated[condecimal(gt=0), Field(description="Decimal value greater than 0")]
PositiveInt = Annotated[conint(gt=0), Field(description="int value greater than 0")]

fake = Faker()

# 🧱 DAO Model
class DAOModel(BaseModel):
    property_id: str
    name: str
    link: HttpUrl
    description: str
    dao_type: str
    operational_scope: str
    valuation: PositiveDecimal
    currency: UppercaseChar
    total_token_supply: PositiveInt
    treasury_address: str
    voting_token_address: str
    governance_model: str

def generate_fake_daos(property_pairs: List[List[str]]) -> List[DAOModel]:
    dao_types = ['single_property', 'multi_property', 'contractor', 'hedge_fund', 'realtor_team', 'reit', 'developer', 'community', 'guild', 'foundation', 'investor_club']
    scopes = ['local', 'regional', 'national', 'global']
    daos = []
    
    for prop_pair in property_pairs:
        daos.append(DAOModel(
            property_id=prop_pair[0],
            name=fake.company() + " DAO",
            link=HttpUrl(fake.url()),
            description=fake.paragraph(),
            dao_type=random.choice(dao_types),
            operational_scope=random.choice(scopes),
            valuation=Decimal(round(random.uniform(1_000_000, 100_000_000), 2)),
            currency="USD",
            total_token_supply=random.randint(1_000_000, 1_000_000_000),
            treasury_address=fake.sha256(),
            voting_token_address=fake.sha256(),
            governance_model=random.choice(["1-token-1-vote", "quadratic", "liquid"])
        ))
    return daos

def insert_fake_daos(daos: List[DAOModel]) -> List[List[str]]:
    inserted_ids: List[List[str]] = []
    for dao in daos:
        try:
            dao_data = dao.model_dump()
            dao_data["link"] = str(dao_data["link"])
            dao_data["valuation"] = str(dao_data["valuation"])
            response = supabase_bot.table("daos").upsert(dao_data).execute()
            inserted = response.data[0]
            print(f"✅ Inserted DAO: {inserted['name']} (ID: {inserted['id']}) (PROP_ID: {inserted['property_id']})")
            inserted_ids.append([inserted["id"], inserted["property_id"]])
        except Exception as e:
            print(f"❌ Error inserting DAO {dao.name}: {e}")
    return inserted_ids

if __name__ == "__main__":
    # Dummy property pairs (property_id, user_id) — only property_id needed here
    dummy_property_ids = [[str(uuid.uuid4()), str(uuid.uuid4())] for _ in range(3)]
    daos_data = generate_fake_daos(dummy_property_ids)
    insert_fake_daos(daos_data)
    print("🏁 DAOs data generation and insertion complete.")
