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
- [x] Create `User`, `ActivityModel`, etc. using Pydantic v2
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

### Deployment Considerations for Federated Schema

Since the subgraphs are currently defined within a single application, the deployment strategy focuses on deploying this application and its interaction with an external Apollo Gateway.

*   **Service Discovery:** The Apollo Gateway needs to discover the network address of this service. This can be achieved through:
    *   **Service Registry:** Using a service registry (e.g., Consul, etcd) where the application registers itself.
    *   **DNS:** Configuring DNS entries that the gateway can resolve.
    *   **Static Configuration:** Manually configuring the gateway with the service's address (suitable for simpler setups).
*   **Scalability and Load Balancing:** To handle increased traffic, multiple instances of this application can be deployed behind a load balancer. The load balancer would distribute incoming requests from the gateway across the instances.
*   **Configuration Management:** Environment variables (like database connection strings, API keys, and the `STORAGE_ENGINE` setting) need to be securely managed in the production environment. This can be done using:
    *   **Environment Variables:** Set directly in the hosting environment.
    *   **Secret Management Systems:** Using systems like HashiCorp Vault, AWS Secrets Manager, or Kubernetes Secrets.

---

## Architectural Review

Based on the project structure and key files examined, the project follows a **Layered Architecture** with distinct layers for Presentation (Schema/Resolvers), Application/Service, and Data Access (Adapters).

**Key Observations:**

- Uses FastAPI with Strawberry GraphQL.
- Integrates with Supabase, Google Cloud Firestore, and Redis via an Adapter pattern (`AbstractStorageAdapter`).
- Authentication is handled at the middleware level.
- GraphQL resolvers for user operations currently interact directly with adapters, bypassing the designated Service Layer (`app/services/user_service.py`).

**Design Patterns Identified:**

- **Adapter Pattern:** Provides a common interface for different storage implementations.
- **Middleware Pattern:** Used for authentication.
- **Repository Pattern (Implicit):** Adapters function similarly to repositories.
- **Code-First GraphQL Schema:** Schema defined in Python code using Strawberry.

**Architectural Flow:**

```mermaid
graph TD
    A[Client] --> B(FastAPI App);
    B --> C{Auth Middleware};
    C --> D(GraphQL Router);
    D --> E[Resolvers];
    E --> F(Services);
    F --> G(Adapters);
    G --> H[Data Sources<br>(Firestore, Supabase, Redis)];
    C -- Authenticated Request --> D;
    D -- GraphQL Query/Mutation --> E;
    E -- Business Logic --> F;
    F -- Data Access --> G;
```

---

## 🧪 Optional Enhancements

- [x] Add MongoDBAdapter (via `motor`) - Implemented
- [ ] Add DynamoDBAdapter (via `aioboto3`)
- [x] Federation support (Apollo Gateway-compatible) - Implemented (subgraphs defined within current app)
- [ ] Caching directives in GraphQL layer
- [ ] Rate limiting middleware
- [ ] Admin CLI for manual adapter switch


<!-- TODO reate limiting in supabase with upstash redis rate limiting -->
<!-- Use resend for emails https://www.youtube.com/watch?v=Qf7XvL1fjvo -->
<!-- Use Hono cloudflare to speed up api -->
