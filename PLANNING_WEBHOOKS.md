# Detailed Plan for Webhook & Real-time Integration (with Celery)

The goal is to build a robust, scalable, and secure event notification system that combines the flexibility of webhooks with the low-latency capabilities of WebSockets, allowing various components (internal or external) to subscribe to and receive notifications about significant events within the `api-central` application.

## Phase 1: Core Webhook Infrastructure (for general events)

1.  **Define Webhook Data Model**:
    *   Create a new database model (e.g., `app/models/webhook.py`) to store webhook subscriptions.
    *   Fields will include: `id`, `target_url`, `event_type` (e.g., `auction.completed`, `user.registered`), `secret`, `owner_id` (Optional), `is_active`, `created_at`, `updated_at`, `headers` (Optional).

2.  **Persistence Layer Integration**:
    *   Integrate the `Webhook` model with existing database adapters.

3.  **Webhook Service (`app/services/webhook_service.py`)**:
    *   Implement CRUD operations for webhook management.

4.  **API Endpoints (`app/schema/resolvers/webhook_resolver.py`)**:
    *   Expose GraphQL mutations and queries for webhook management, ensuring proper authentication and authorization.

## Phase 2: Real-time Streaming Infrastructure (for low-latency events)

1.  **WebSocket Server Integration**:
    *   Integrate a WebSocket server into the `app/main.py` or a dedicated module (e.g., `app/realtime/websocket_manager.py`). This will allow clients to establish persistent connections.
    *   Consider using a library like `websockets` or `FastAPI`'s WebSocket capabilities if the project is Python/FastAPI based.

2.  **Real-time Event Broadcasting Mechanism**:
    *   Implement a mechanism to broadcast events to all connected WebSocket clients. This will involve a **Redis Pub/Sub channel**: Services publish events to Redis, and the WebSocket server subscribes to these channels and broadcasts to clients. This decouples the event source from the WebSocket server and allows for horizontal scaling.

3.  **Client Subscription Management**:
    *   Allow WebSocket clients to subscribe to specific event types (e.g., `trade.submitted`, `snft.price_changed`) or specific SNFT IDs.
    *   Manage active WebSocket connections and their subscriptions.

## Phase 3: Unified Event Dispatching & Publishing

1.  **Identify Key Events**:
    *   Review existing services to identify critical state changes.
    *   Categorize events:
        *   **High-Frequency/Low-Latency Events**: `trade.submitted`, `trade.price_changed`, `order_book.updated` (if applicable). These will primarily go to the WebSocket broadcasting system via Redis Pub/Sub.
        *   **General Events**: `auction.created`, `auction.completed`, `user.registered`, `transaction.processed`. These will primarily go to the HTTP webhook system via Celery. Some events might go to both.

2.  **Central Event Publisher (`app/utils/event_publisher.py` or `app/services/event_publisher_service.py`)**:
    *   A central component that services will call when an event occurs.
    *   It will:
        *   Receive an event (`event_type`, `payload`).
        *   **For HTTP Webhooks**: Query the database for active webhooks subscribed to that `event_type` and dispatch them as tasks to **Celery**.
        *   **For WebSockets**: Publish the event to the **Redis Pub/Sub channel**.

3.  **Instrument Services**:
    *   Modify relevant service methods to call the `Event Publisher` after a significant event occurs.

4.  **Celery Task for Webhook Delivery**:
    *   Define a Celery task (e.g., `app/tasks/webhook_tasks.py`) responsible for making the HTTP POST request to the `target_url`.
    *   **Payload Construction**: Standardize the webhook payload format.
    *   **Payload Signing**: Implement HMAC-SHA256 signing.
    *   **Retry Logic**: Leverage Celery's built-in retry mechanisms with exponential backoff for failed deliveries.
    *   **Logging**: Log every delivery attempt, success, and failure within the Celery task.

## Phase 4: Security, Reliability & Monitoring

1.  **Payload Signing & Verification**:
    *   For HTTP webhooks, ensure `secret` is securely generated and stored, and provide documentation for signature verification.

2.  **WebSocket Security**:
    *   Implement authentication for WebSocket connections (e.g., JWT token passed during handshake).
    *   Rate limiting for WebSocket connections.

3.  **Error Handling & Dead-Letter Queue (DLQ)**:
    *   For HTTP webhooks, configure Celery to handle persistent failures, potentially moving them to a "dead-letter" state or a separate queue for manual inspection.
    *   For WebSockets, handle disconnections gracefully and implement client-side reconnect logic.

4.  **Monitoring and Alerting**:
    *   Set up metrics for both HTTP webhook deliveries (success/failure, latency, Celery queue depth) and WebSocket connections (active connections, message throughput, errors).
    *   Configure alerts for high failure rates or prolonged delays.

5.  **Scalability**:
    *   Ensure the WebSocket server, Redis, and Celery workers can scale horizontally to handle high concurrent connections and message volumes.

## Phase 5: Documentation & External Consumption

1.  **Developer Documentation**:
    *   Create comprehensive documentation for external developers on:
        *   How to register HTTP webhooks (API endpoints, available event types, signature verification).
        *   How to connect to the WebSocket server, subscribe to real-time events, and understand payload structures for high-frequency updates.
        *   Delivery guarantees and best practices for both systems.

## Architectural Diagram

```mermaid
graph TD
    subgraph API Central Application
        A[User/Internal Service] --> B(GraphQL API);
        B --> C[Webhook Resolver];
        C --> D[Webhook Service];
        D --> E[Database (Webhook Model)];

        F[Core Services (e.g., TradeService)] --> G[Event Publisher];
        G --> H[Celery Task Queue (for HTTP Webhooks)];
        H --> I[Celery Worker (HTTP Webhook Sender)];
        I --> J[External Webhook URL];

        G --> K[Real-time Event Broker (Redis Pub/Sub)];
        K --> L[WebSocket Server];
        L --> M[Connected WebSocket Clients];
    end

    E --> G; % Event Publisher retrieves webhooks from DB
    I --> N[Logging & Monitoring];
    I --> O[Celery Retry Mechanism];
    O --> I; % Retries go back to Celery Worker
    O --> P[Dead-Letter Queue (Optional)];

    L --> N; % WebSocket logging
    L --> Q[WebSocket Connection Management];

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#f9f,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333,stroke-width:2px
    style J fill:#f9f,stroke:#333,stroke-width:2px
    style K fill:#bbf,stroke:#333,stroke-width:2px
    style L fill:#bbf,stroke:#333,stroke-width:2px
    style M fill:#f9f,stroke:#333,stroke-width:2px
    style N fill:#f9f,stroke:#333,stroke-width:2px
    style O fill:#bbf,stroke:#333,stroke-width:2px
    style P fill:#f9f,stroke:#333,stroke-width:2px
    style Q fill:#bbf,stroke:#333,stroke-width:2px
```
<line_count>179</line_count>
