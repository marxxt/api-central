import re
import uuid
import random
from datetime import timezone
from typing import Annotated, List, Optional, Tuple
from pydantic import BaseModel, HttpUrl, Field, conint, constr
from faker import Faker
from db_utils import supabase_bot

ThreeChLong = Annotated[constr(min_length=3, max_length=3), Field(description="String is no longer nor less than 3 characters")]
PositiveInt = Annotated[conint(gt=0), Field(description="int value greater than 0")]

fake = Faker()
class SNFTModel(BaseModel):
    wallet_id: Optional[str]
    owner_id: Optional[str]
    name: str
    description: str
    image_url: HttpUrl
    price: float
    currency: str
    address: str
    creator: str
    date_listed: str
    category: str
    collection_id: Optional[str]
    metadata_status: str
    status: str
    property_id: str
    contract_address: str
    dao_id: str
    trust_id: Optional[str]
    total_tokens: PositiveInt
    apy: float
    token_symbol: ThreeChLong
    tokens_sold: int
    token_price: float
    sale_status: str
    metadata_uri: HttpUrl
    metadata_hash: str
    legal_doc_urls: Optional[dict]
    notarization_status: str
    wizard_progress: dict
    deployed_at: Optional[str]
    preview_uri: Optional[str]
    expires_at: str

class SNFTArray(BaseModel):
    snfts_data: SNFTModel
    dao_id: str
class SNFTResponse(BaseModel):
    data: List[SNFTArray]
    
def generate_fake_snfts(wallet_pairs, property_pairs, collection_ids, dao_triplets, ) -> SNFTResponse:
    print("Generating SNFTS")
    snfts: List[SNFTArray] = []
    statuses = ['draft', 'property_added', 'docs_uploaded', 'pending_signature', 'notarized', 'metadata_ready', 'minted']
    sale_statuses = ['open', 'closed', 'paused']
    num_snfts_per_property = 1

    for dao in dao_triplets:
        dao_id: str = dao[0]
        prop_id = dao[1]
        
        # Find matching property contain user_id for owner
        prop_pair = next((pair for pair in property_pairs if pair[0] == prop_id), None)
        print(f" Searching for {prop_id} in {prop_pair}")
        if not prop_pair:
            continue
        
        # Find  wallet belonging to owner
        owner = prop_pair[1]
        wallet_pair = next((pair for pair in wallet_pairs if pair[1] == owner), None)
        if not wallet_pair:
            continue
        wallet = wallet_pair[0]
        for _ in range(num_snfts_per_property):
            name = fake.word().capitalize()
            symbol = fake.unique.lexify(
                text="???", 
                letters=re.sub(r"\s+", "", name).upper()
            )
            data: SNFTModel = SNFTModel(
                    wallet_id=wallet,
                    owner_id=owner,
                    name=name + " SNFT",
                    description=fake.paragraph(),
                    image_url=HttpUrl("https://via.placeholder.com/400"),
                    price=round(random.uniform(1000, 100000), 2),
                    currency=random.choice(["USD", "ETH", "USDC"]),
                    address=fake.address(),
                    creator=fake.name(),
                    date_listed=fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc).isoformat(),
                    category=fake.word(),
                    collection_id=random.choice(collection_ids) if collection_ids else None,
                    metadata_status=random.choice(['complete', 'pending', 'failed']),
                    status=random.choice(statuses),
                    property_id=prop_pair[0],
                    contract_address=fake.sha256(),
                    dao_id=dao_id,
                    trust_id=str(uuid.uuid4()) if random.random() > 0.5 else None,
                    token_symbol=symbol,
                    total_tokens=random.randint(10000, 1000000),
                    tokens_sold=random.randint(0, 50000),
                    token_price=round(random.uniform(0.1, 10.0), 2),
                    apy=round(random.uniform(0.03, 0.15), 4),
                    sale_status=random.choice(sale_statuses),
                    metadata_uri=HttpUrl(fake.url()),
                    metadata_hash=fake.sha256(),
                    legal_doc_urls={"trust_agreement": fake.url(), "dao_agreement": fake.url()} if random.random() > 0.5 else None,
                    notarization_status=random.choice(['pending', 'complete', 'rejected']),
                    wizard_progress={"step": random.randint(1, 5), "completed": random.sample(['property', 'images', 'docs', 'mint'], k=random.randint(0, 4))},
                    deployed_at=fake.date_time_between(start_date="-6m", end_date="now", tzinfo=timezone.utc).isoformat() if random.random() > 0.3 else None,
                    preview_uri=fake.url() if random.random() > 0.2 else None,
                    expires_at=fake.date_time_between(start_date="now", end_date="+6m", tzinfo=timezone.utc).isoformat()
                )
            result: SNFTArray = SNFTArray(snfts_data=data, dao_id=dao_id)
            snfts.append(
               result
            )

    return SNFTResponse(data=snfts)

def insert_fake_snfts(snfts: SNFTResponse) -> List[Tuple[str, str,str]]:
    snft_ids: List[Tuple[str, str,str]] = []
    for snft in snfts.data:
        model = snft.snfts_data
        try:
            snft_data = model.model_dump(exclude_none=True)
            snft_data["image_url"] = str(snft_data["image_url"])
            snft_data["metadata_uri"] = str(snft_data["metadata_uri"])
            response = supabase_bot.table("snfts").upsert(snft_data).execute()
            inserted_id = response.data[0]["id"]
            print(f"✅ Inserted SNFT: {model.name} -> {inserted_id}")
            res = (inserted_id, snft_data["token_symbol"], snft_data["owner_id"])
            snft_ids.append(res)
        except Exception as e:
            print(f"❌ Error inserting SNFT {model.name}: {e}")
    return snft_ids

if __name__ == "__main__":
    pass
