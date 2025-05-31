import uuid
import random
from datetime import timezone
from faker import Faker
from config import supabase_bot

fake = Faker()

PROPERTY_IMAGE_POOL = [
    "apartment-complex.jpg",
    "beachfront-villa.jpg",
    "brownstone.jpg",
    "commercial-real-estate.jpg",
    "downtown-penthouse.jpg",
    "luxury-beachfront-villa.jpg",
    "luxury-villa.jpg",
    "miami-luxury.jpg",
    "mountain-cabin.jpg",
    "mountain-retreat.jpg",
    "office-building.jpg",
    "property-1.jpg",
    "property-2.jpg",
    "property-3.jpg",
    "property-4.jpg",
    "property-5.jpg",
    "property-6.jpg",
    "retail-shopping-center.jpg",
    "seaside-cottage.jpg",
    "waterfront-apartments-complex.jpg"
]

def generate_fake_properties(user_ids, num_properties_per_user=3):
    properties = []
    property_types = ['SFR', 'MultiFamily', 'Commercial']
    statuses = ['For Sale', 'Rented', 'Pending']
    for user_id in user_ids:
        for _ in range(num_properties_per_user):
            name = fake.company() + " Property"
            image_file = random.choice(PROPERTY_IMAGE_POOL)
            properties.append({
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "name": name,
                "token_symbol": fake.unique.lexify(text="???", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
                "description": fake.paragraph(),
                "image_url": f"images/{image_file}",
                "address": fake.address(),
                "property_type": random.choice(property_types),
                "status": random.choice(statuses),
                "valuation": round(random.uniform(100_000, 5_000_000), 2),
                "total_tokens": random.randint(1000, 100000),
                "apy": round(random.uniform(0.03, 0.15), 4),
                "date_listed": fake.date_time_between(start_date="-2y", end_date="now", tzinfo=timezone.utc).isoformat()
            })
    return properties


def insert_fake_properties(properties):
    property_ids = []
    for prop in properties:
        try:
            response = supabase_bot.table("properties").upsert(prop).execute()
            inserted = response.data[0]
            print(f"🏠 Inserted property: {inserted['name']} with id: {inserted['id']}")
            property_ids.append(inserted["id"])
        except Exception as e:
            print(f"❌ Error inserting property {prop['name']}: {e}")
    return property_ids

if __name__ == "__main__":
    dummy_user_ids = [str(uuid.uuid4()) for _ in range(3)]
    properties_data = generate_fake_properties(dummy_user_ids)
    insert_fake_properties(properties_data)
    print("✅ Properties data generation and insertion complete.")
