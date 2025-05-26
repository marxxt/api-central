# Planning – Storage-Agnostic GraphQL API Gateway

## 📆 Phase 1: Project Bootstrap

- [ ] Initialize project using `poetry`
- [ ] Create basic FastAPI app
- [ ] Set up GraphQL with Strawberry
- [ ] Add `.env` support with PydanticSettings
- [ ] Define folder structure:
  - `/auth`
  - `/adapters`
  - `/models`
  - `/schema`
  - `/services`
  - `/tests`

---

## 📆 Phase 2: Core Interfaces & Models

- [ ] Define `AbstractStorageAdapter` (with `get_user`, `store_user`)
- [ ] Create `UserModel`, `ActivityModel`, etc. using Pydantic v2
- [ ] Define reusable error/exception classes

---

## 📆 Phase 3: Adapter Implementations

- [ ] `SupabaseAdapter` using REST/SDK
- [ ] `RedisAdapter` using `redis.asyncio`
- [ ] `FirestoreAdapter` using `google-cloud-firestore`

---

## 📆 Phase 4: Authentication

- [ ] Middleware to decode and verify Supabase JWTs
- [ ] Inject user info into `request.state.user`
- [ ] Protect resolvers with authorization guard

---[x

## 📆 Phase 5: GraphQL Schema

- [ ] Define schema and types with Strawberry
- [ ] Add resolvers for:
  - `get_user`
  - `get_recent_activity`
  - `store_user_data`
- ] Validate all resolver IO through Pydantic

---

## 📆 Phase 6: Environment & Runtime Config

- [ ] Add support for `.env` and runtime config
- [ ] Switch active adapter based on ENV (e.g. FIREBASE vs SUPABASE)

---

## 📆 Phase 7: Testing

- [ ] Add `pytest` configuration
- [ ] Mock adapters for unit tests
- [ ] Write tests for:
  - Auth flow
  - GraphQL resolver logic
  - Adapter edge cases (fallback, 404s, cache misses)

---

## 📆 Phase 8: Docker & DevOps

- [ ] Create `Dockerfile`
- [ ] Write `docker-compose.yml` for local development
- [ ] Add health checks and startup logging

---

## 🧪 Optional Enhancements

- [ ] Add MongoDBAdapter (via `motor`)
- [ ] Add DynamoDBAdapter (via `aioboto3`)
- [ ] Federation support (Apollo Gateway-compatible)
- [ ] Caching directives in GraphQL layer
- [ ] Rate limiting middleware
- [ ] Admin CLI for manual adapter switch
