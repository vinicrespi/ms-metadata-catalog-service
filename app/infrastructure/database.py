from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from pymongo import AsyncMongoClient

from app.adapters.outbound.mongodb_metadata_repository import MongoMetadataRepository
from app.application.ports.repositories import MetadataRepositoryPort
from app.application.use_cases.services import MetadataService
from app.infrastructure.config import Settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    settings = Settings()
    client = AsyncMongoClient(settings.mongodb_url)
    app.state.mongo_client = client
    app.state.metadata_repository = MongoMetadataRepository(client, settings.mongodb_database)
    yield
    await client.close()


def get_metadata_service(request: Request) -> MetadataService:
    repository: MetadataRepositoryPort = request.app.state.metadata_repository
    return MetadataService(repository)