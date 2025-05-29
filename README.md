# 🧠 Bridges Market Central API

This project is a modular, **storage-agnostic GraphQL API gateway** built with:

- **FastAPI** for HTTP runtime
- **Strawberry GraphQL** for a type-safe schema
- **Pydantic v2** for model validation
- **Supabase**, **Redis**, and **Firestore** as interchangeable storage adapters

---

## 📦 Architecture Overview

### 🔁 Adapter-Based Persistence

All data operations flow through a common interface:

```python
class AbstractStorageAdapter:
    async def get_user(self, id: str) -> UserModel: ...
    async def store_user(self, user: UserModel): ...
Adapters implemented:

SupabaseAdapter

RedisAdapter

FirestoreAdapter

CachingAdapter (wraps Redis + Supabase/Firestore)

Switchable via .env config:

ini
Always show details

Copy
STORAGE_ENGINE=SUPABASE | FIRESTORE | REDIS
🧱 Schema + Models
All data is modeled in app/models/ using Pydantic v2. GraphQL types are defined in app/schema/types/.

Domain	Models
user	User, Wallet, Profile, Reputation
snft	SNFT, Transaction
auction	BidHistory, Seller, PropertyDetails
trade	PropertyListing, OrderFormState
index	MarketplaceItem, CollectionItem

Each has a corresponding GraphQL type (UserType, WalletType, etc).

📡 GraphQL Schema
Schema is composed from resolvers in app/schema/resolvers/, grouped by domain. You can access the interactive GraphQL playground at:

bash
Always show details

Copy
http://localhost:3000/graphql
Example query:

graphql
Always show details

Copy
query {
  user(id: "abc123") {
    id
    firstName
    wallets {
      balance
    }
  }
}
🔐 Auth
JWT auth middleware checks for Authorization: Bearer <token> header.

In development, unauthenticated access is allowed for:

/

/graphql (GET only)

/health

🐳 Dev Setup
Install Python 3.11+

Install Poetry:

bash
Always show details

Copy
curl -sSL https://install.python-poetry.org | python3 -
Install deps:

bash
Always show details

Copy
poetry install
Run dev server:

bash
Always show details

Copy
poetry run python app/main.py
🧪 Tests
Tests are located under tests/ and use pytest. To run:

bash
Always show details

Copy
poetry run pytest
Adapters are mocked to test GraphQL and async flows.

📁 Project Structure
graphql
Always show details

Copy
app/
├── adapters/              # Storage engines
├── auth/                  # Supabase JWT middleware
├── models/                # Pydantic v2 schemas
├── schema/
│   ├── types/             # GraphQL types (Strawberry + Pydantic)
│   ├── resolvers/         # Per-domain resolvers
│   └── schema.py          # Root export
└── main.py                # FastAPI + GraphQL app
📄 License
MIT © Bridges Market Team