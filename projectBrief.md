🧠 projectBrief.md
🏷️ Project Name
Bridges Market Central API

🎯 Purpose
Develop a modular, storage-agnostic GraphQL API gateway that aggregates data from multiple backend sources, including Supabase (SQL), Firestore (NoSQL), Redis (cache), and external microservices. The API should provide a unified interface for clients, ensuring scalability, maintainability, and ease of integration.

🏗️ Architecture Overview
Framework: FastAPI

GraphQL: Strawberry

Data Validation: Pydantic v2

Authentication: Supabase JWT via middleware

Storage Adapters:

SupabaseAdapter (SQL)

FirestoreAdapter (NoSQL)

RedisAdapter (Cache)

Adapter Pattern: All storage adapters implement AbstractStorageAdapter interface.

Environment Configuration: Supports .env files with PydanticSettings.

Runtime Adapter Switching: Based on STORAGE_ENGINE environment variable.

🔐 Authentication Strategy
Implement middleware to decode and verify Supabase JWTs.

Inject user information into request.state.user.

Protect GraphQL resolvers with authorization guards based on user roles.

📦 Key Features
GraphQL-Only API Surface: No REST endpoints required.

Storage Backend Abstraction: Enables portability across different storage solutions.

Unified Data Models: Utilize Pydantic models for consistent data contracts.

Asynchronous Architecture: Ensure non-blocking I/O operations.

CI/CD Integration: Containerized with Docker and managed via docker-compose.

Runtime Configuration: Switch active adapters based on environment settings.

🧪 Testing Strategy
Utilize pytest for unit and integration tests.

Mock adapters to simulate different storage backends.

Test scenarios include:

Authentication flows

GraphQL resolver logic

Adapter edge cases (e.g., fallback mechanisms, 404s, cache misses)

🚀 Deployment Considerations
Service Discovery: Integrate with Apollo Gateway using service registry, DNS, or static configuration.

Scalability: Deploy multiple instances behind a load balancer to handle increased traffic.

Configuration Management: Manage environment variables and secrets securely using tools like HashiCorp Vault or AWS Secrets Manager.

📁 Project Structure
csharp
Copy
Edit
api-central/
├── app/
│   ├── adapters/
│   │   ├── base.py
│   │   ├── supabase_adapter.py
│   │   ├── firestore_adapter.py
│   │   └── redis_adapter.py
│   ├── auth/
│   │   ├── middleware.py
│   │   └── utils.py
│   ├── models/
│   │   ├── user.py
│   │   ├── auction.py
│   │   ├── trade.py
│   │   └── ...
│   ├── schema/
│   │   ├── types/
│   │   └── resolvers/
│   ├── services/
│   │   ├── user_service.py
│   │   └── ...
│   └── main.py
├── tests/
│   ├── test_auth.py
│   ├── test_adapters/
│   ├── test_models/
│   └── test_services/
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
🧩 Future Enhancements
Implement additional adapters (e.g., MongoDBAdapter, DynamoDBAdapter).

Add support for GraphQL federation compatible with Apollo Gateway.

Introduce caching directives in the GraphQL layer.

Implement rate limiting middleware.

Develop an admin CLI for manual adapter switching.