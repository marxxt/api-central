from decimal import Decimal
import uuid
import random
from datetime import timezone
from typing import Annotated, List
from pydantic import BaseModel, UUID4, Field, constr, condecimal, conint
from faker import Faker
from config import supabase_bot

PositiveDecimal = Annotated[condecimal(gt=0), Field(description="Decimal value greater than 0")]
PositiveInt = Annotated[conint(gt=0), Field(description="int value greater than 0")]

fake = Faker()

PROPERTY_IMAGE_POOL = [
    "apartment-complex.jpg", "beachfront-villa.jpg", "brownstone.jpg",
    "commercial-real-estate.jpg", "downtown-penthouse.jpg", "luxury-beachfront-villa.jpg",
    "luxury-villa.jpg", "miami-luxury.jpg", "mountain-cabin.jpg", "mountain-retreat.jpg",
    "office-building.jpg", "property-1.jpg", "property-2.jpg", "property-3.jpg",
    "property-4.jpg", "property-5.jpg", "property-6.jpg", "retail-shopping-center.jpg",
    "seaside-cottage.jpg", "waterfront-apartments-complex.jpg"
]

# 🧱 Property model
class PropertyModel(BaseModel):
    user_id: str
    name: str
    description: str
    image_url: str
    address: str
    property_type: str
    status: str
    valuation: PositiveDecimal
    date_listed: str  # ISO format string

def generate_fake_properties(user_ids: List[str], num_properties_per_user: int = 1) -> List[PropertyModel]:
    properties = []
    property_types = ['SFR', 'MultiFamily', 'Commercial']
    statuses = ['For Sale', 'Rented', 'Pending']
    for user_id in user_ids:
        for _ in range(num_properties_per_user):
            name = fake.company() + " Property"
            image_file = random.choice(PROPERTY_IMAGE_POOL)
            properties.append(PropertyModel(
                user_id=user_id,
                name=name,
                description=fake.paragraph(),
                image_url=f"images/{image_file}",
                address=fake.address(),
                property_type=random.choice(property_types),
                status=random.choice(statuses),
                valuation=Decimal(round(random.uniform(100_000, 5_000_000), 2)),
                date_listed=fake.date_time_between(start_date="-2y", end_date="now", tzinfo=timezone.utc).isoformat()
            ))
    return properties

def insert_fake_properties(properties: List[PropertyModel]) -> List[List[str]]:
    property_ids = []
    for prop in properties:
        try:
            property_data = prop.model_dump()
            property_data["valuation"] = str(property_data["valuation"])
            response = supabase_bot.table("properties").upsert(property_data).execute()
            inserted = response.data[0]
            print(f"🏠 Inserted property: {inserted['name']} with id: {inserted['id']} for user: {inserted['user_id']} ")
            property_ids.append([inserted["id"], inserted["user_id"]])
        except Exception as e:
            print(f"❌ Error inserting property {prop.name}: {e}")
    return property_ids

if __name__ == "__main__":
    dummy_user_ids = [str(uuid.uuid4() for _ in range(3))]
    properties_data = generate_fake_properties(dummy_user_ids)
    insert_fake_properties(properties_data)
    print("✅ Properties data generation and insertion complete.")
