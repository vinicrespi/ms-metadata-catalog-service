from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pymongo import AsyncMongoClient

from app.adapters.outbound.history_adapter import MongoHistoryAdapter
from app.adapters.outbound.metadata_adapter import MongoMetadataAdapter
from app.adapters.outbound.user_adapter import MongoUserAdapter
from app.infrastructure.config import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = Settings()
    client = AsyncMongoClient(settings.DATABASE_URL)
    app.state.mongo_client = client
    app.state.history_repository = MongoHistoryAdapter(client, settings.DATABASE_NAME)
    app.state.user_repository = MongoUserAdapter(client, settings.DATABASE_NAME)
    await app.state.user_repository.initialize()
    app.state.metadata_repository = MongoMetadataAdapter(
        client, settings.DATABASE_NAME, app.state.history_repository
    )
    yield
    await client.close()
