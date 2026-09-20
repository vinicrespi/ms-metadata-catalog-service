from typing import Any, Optional

from app.application.ports.repositories import MetadataRepositoryPort
from app.domain.models import MetadataCreate


class MetadataService:

    def __init__(self, repository: MetadataRepositoryPort) -> None:
        self._repository = repository

    async def create(self, data: MetadataCreate) -> dict[str, Any]:
        return await self._repository.create(data)
