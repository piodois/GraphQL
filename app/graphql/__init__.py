import strawberry
from .resolvers import Query, Mutation

# Crear el esquema GraphQL
schema = strawberry.Schema(query=Query, mutation=Mutation)

__all__ = ["schema"]