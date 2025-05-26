# Planning – Storage-Agnostic GraphQL API Gateway

## 📆 Phase 1: Project Bootstrap

- [x] Initialize project using `poetry`
- [x] Create basic FastAPI app
- [x] Set up GraphQL with Strawberry
- [x] Add `.env` support with PydanticSettings
- [x] Define folder structure:
  - `/auth`
  - `/adapters`
  - `/models`
  - `/schema`
  - `/services`
  - `/tests`

---

## 📆 Phase 2: Core Interfaces & Models

- [x] Define `AbstractStorageAdapter` (with `get_user`, `store_user`)
- [x] Create `UserModel`, `ActivityModel`, etc. using Pydantic v2
- [x] Define reusable error/exception classes

---

## 📆 Phase 3: Adapter Implementations

- [x] `SupabaseAdapter` using REST/SDK
- [x] `RedisAdapter` using `redis.asyncio`
- [x] `FirestoreAdapter` using `google-cloud-firestore`

---

## 📆 Phase 4: Authentication

- [x] Middleware to decode and verify Supabase JWTs
- [x] Inject user info into `request.state.user`
- [x] Protect resolvers with authorization guard

---

## 📆 Phase 5: GraphQL Schema

- [x] Define schema and types with Strawberry
- [x] Add resolvers for:
  - `get_user`
  - `get_recent_activity`
  - `store_user_data`
- [x] Validate all resolver IO through Pydantic

---

## 📆 Phase 6: Environment & Runtime Config

- [x] Add support for `.env` and runtime config
- [x] Switch active adapter based on ENV (e.g. FIREBASE vs SUPABASE)

---

## 📆 Phase 7: Testing

- [x] Add `pytest` configuration
- [x] Mock adapters for unit tests
- [x] Write tests for:
  - Auth flow
  - GraphQL resolver logic
  - Adapter edge cases (fallback, 404s, cache misses)

---

## 📆 Phase 8: Docker & DevOps

- [x] Create `Dockerfile`
- [x] Write `docker-compose.yml` for local development
- [x] Add health checks and startup logging

---

## 🧪 Optional Enhancements

- [ ] Add MongoDBAdapter (via `motor`)
- [ ] Add DynamoDBAdapter (via `aioboto3`)
- [ ] Federation support (Apollo Gateway-compatible)
- [ ] Caching directives in GraphQL layer
- [ ] Rate limiting middleware
- [ ] Admin CLI for manual adapter switch
