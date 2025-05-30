# Product Context – Bridges Market Central API

## 🎯 Purpose
Develop a modular, storage-agnostic GraphQL API gateway that aggregates data from multiple backend sources, including Supabase (SQL), Firestore (NoSQL), Redis (cache), and external microservices. The API should provide a unified interface for clients, ensuring scalability, maintainability, and ease of integration.

## 👥 Target Users
- Frontend developers building applications for Bridges Market.
- Internal services requiring unified data access.
- External partners integrating with Bridges Market's platform.

## 🛠 Problems Addressed
- Disparate data sources leading to complex integrations.
- Inconsistent data models across services.
- Difficulty in scaling and maintaining multiple APIs.

## 🌟 Key Features
- Unified GraphQL API surface.
- Pluggable storage adapters for flexibility.
- Middleware-based authentication using Supabase JWTs.
- Environment-based configuration for adapter selection.

## 🔍 Success Metrics
- Reduced integration time for new services.
- Improved data consistency across applications.
- Enhanced developer experience through simplified API access.
