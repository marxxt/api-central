# Technical Context – Bridges Market Central API

## 🖥 Programming Language
- Python 3.11+

## 🧰 Frameworks & Libraries
- **FastAPI**: Web framework for building APIs.
- **Strawberry**: Library for building GraphQL APIs.
- **Pydantic v2**: Data validation and settings management.
- **Poetry**: Dependency management and packaging.

## 🗄 Storage Backends
- **Supabase**: SQL database accessed via REST/SDK.
- **Firestore**: NoSQL document database.
- **Redis**: In-memory data structure store for caching.

## 🔐 Authentication
- **Supabase JWT**: Used for authenticating API requests.
- **Middleware**: Processes JWTs and injects user context into requests.

## ⚙ Configuration
- **.env Files**: Manage environment-specific settings.
- **PydanticSettings**: Load and validate configuration from environment variables.

## 🧪 Testing
- **Pytest**: Framework for writing and running tests.
- **Mocking**: Adapters and services are mocked for unit testing.

## 🐳 Containerization
- **Docker**: Containerize the application for consistent environments.
- **Docker Compose**: Define and run multi-container Docker applications.
