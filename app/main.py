import os
import uvicorn
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from app.schema.resolvers import schema
from app.auth.middleware import SupabaseAuthMiddleware
from app.config import settings

# Initialize FastAPI app
app = FastAPI()

# Attach Supabase JWT Middleware
app.add_middleware(SupabaseAuthMiddleware)

# Mount GraphQL schema
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
