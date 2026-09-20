from fastapi import Request

from app.application.ports.repositories import MetadataRepositoryPort
from app.application.use_cases.services import MetadataService


def get_metadata_service(request: Request) -> MetadataService:
    repository: MetadataRepositoryPort = request.app.state.metadata_repository
    return MetadataService(repository)
