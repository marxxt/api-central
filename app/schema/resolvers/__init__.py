from app.schema.resolvers.user_resolver import Query, Mutation
import strawberry

schema = strawberry.Schema(query=Query, mutation=Mutation)
