# System Patterns – Bridges Market Central API

## 🏗 Architectural Overview
The system follows a layered architecture:
- **API Layer**: FastAPI with Strawberry for GraphQL.
- **Service Layer**: Business logic encapsulated in service modules.
- **Data Access Layer**: Adapter pattern to interface with various storage backends.

## 🔁 Design Patterns
- **Adapter Pattern**: AbstractStorageAdapter interface implemented by SupabaseAdapter, FirestoreAdapter, and RedisAdapter.
- **Middleware Pattern**: Authentication handled via middleware that processes Supabase JWTs.
- **Factory Pattern**: Adapter instantiation based on environment configuration.

## 🧱 Components
- **Adapters**: Modular connectors to different storage systems.
- **Resolvers**: GraphQL resolvers that delegate to service layer.
- **Services**: Contain business logic and interact with adapters.
- **Models**: Pydantic v2 models defining data schemas.

## 🔄 Data Flow
1. Client sends GraphQL request.
2. Middleware authenticates request.
3. Resolver processes request and calls appropriate service.
4. Service interacts with the selected adapter.
5. Adapter performs data operations and returns results.
