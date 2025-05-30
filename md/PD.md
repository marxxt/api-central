# Project Description – GraphQL Storage-Agnostic Backend API Gateway

## 🧠 Project Name
UniversalGraphQL Gateway (UGG)

## 🎯 Purpose
To develop a modular, scalable GraphQL API backend in Python that aggregates and serves data from multiple backend sources including SQL (Supabase), NoSQL (Firestore), Redis (cache), and external microservices.

## 🏗 Architecture
The system uses:
- **FastAPI** as the HTTP layer
- **Strawberry** for GraphQL schema and query/mutation resolution
- **Pydantic v2** for IO validation and serialization
- **Adapter-based design pattern** to support pluggable data sources

## 🔐 Authentication
- JWT authentication using **Supabase Auth**
- Middleware for request validation and user context injection

## 🧱 Storage Adapters
Each backend type will implement the following:
- `AbstractStorageAdapter`: defines standard methods (`get_user`, `store_user`, etc.)
- `SupabaseAdapter`: SQL via REST or SDK
- `FirestoreAdapter`: NoSQL using `google-cloud-firestore`
- `RedisAdapter`: for short-term cache

## ⚙️ Key Features
- GraphQL-only API surface
- Storage backend abstraction for portability
- Unified user and data model via Pydantic
- Async-ready architecture
- CI/CD and containerized with Docker
- Supports runtime storage engine switching via ENV config

## 🔍 Future Extensions
- Add MongoDB, DynamoDB adapters
- Add GraphQL federation or gateway support
- Extend query batching and caching strategies
- RBAC via Supabase roles or external ACL engine

## 🔐 Compliance
- Token-based auth only (no session cookies)
- No direct DB access from GraphQL layer
- Modular and testable via mocked adapters

## 🧪 Testing Strategy
- Unit tests for adapters and resolvers
- Integration tests with mock or real Redis, Supabase
- Edge case tests: fallback, adapter fail, invalid tokens

## 🛠 Tech Stack

| Layer        | Tool/Library            |
|--------------|--------------------------|
| API Layer    | FastAPI                  |
| Schema       | Strawberry (GraphQL)     |
| Models       | Pydantic v2              |
| SQL Adapter  | Supabase                 |
| NoSQL Adapter| Firestore (Google)       |
| Cache        | Redis                    |
| Auth         | Supabase JWT             |
| Package Mgmt | Poetry                   |
| Testing      | Pytest                   |
| Container    | Docker + Compose         |
