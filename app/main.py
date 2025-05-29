import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from strawberry.fastapi import GraphQLRouter
from app.schema.resolvers import schema # Corrected import path
from app.auth.middleware import AuthMiddleware # Corrected import path
from app.config import settings # Corrected import path
from app.adapters.redis_adapter import RedisAdapter
from app.adapters.mongodb_adapter import MongoDBAdapter
from app.services.webhook_service import WebhookService
from app.utils.event_publisher import EventPublisher, REDIS_PUBSUB_CHANNEL # Import REDIS_PUBSUB_CHANNEL

# Initialize FastAPI app
app = FastAPI(
    title="Bridges Market Central app"
)

# Initialize adapters and services
redis_adapter = RedisAdapter(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)
mongodb_adapter = MongoDBAdapter(
    connection_string=settings.MONGODB_CONNECTION_STRING,
    database_name=settings.MONGODB_DATABASE_NAME
)
webhook_service = WebhookService(storage_adapter=mongodb_adapter)
event_publisher = EventPublisher(webhook_service=webhook_service, redis_client=redis_adapter.client)

# Attach Supabase JWT Middleware
app.add_middleware(AuthMiddleware)

# Mount GraphQL schema
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# WebSocket endpoint for real-time events
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    pubsub = None # Initialize pubsub to None
    try:
        # Subscribe to Redis Pub/Sub channel
        pubsub = redis_adapter.client.pubsub()
        await pubsub.subscribe(REDIS_PUBSUB_CHANNEL) # Use the directly imported constant

        # Keep connection alive and listen for messages
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message:
                await websocket.send_text(message['data'].decode('utf-8'))
            # You can also listen for messages from the client here if needed
            # data = await websocket.receive_text()
            # print(f"Received from client: {data}")
    except WebSocketDisconnect:
        print("Client disconnected from WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if pubsub: # Check if pubsub was initialized
            await pubsub.unsubscribe(REDIS_PUBSUB_CHANNEL) # Use the directly imported constant
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)
