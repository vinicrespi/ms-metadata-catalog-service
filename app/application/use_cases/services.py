from typing import Any, Optional

from app.application.ports.repositories import MetadataRepositoryPort
from app.domain.models import MetadataCreate


class MetadataService:

    def __init__(self, repository: MetadataRepositoryPort) -> None:
        self._repository = repository

    async def create(self, data: MetadataCreate) -> dict[str, Any]:
        return await self._repository.create(data)

    async def get_all(self) -> list[dict[str, Any]]:
        return await self._repository.get_all()

    async def get_by_id(self, metadata_id: str) -> Optional[dict[str, Any]]:
        return await self._repository.get_by_id(metadata_id)

    async def update(self, metadata_id: str, data: MetadataCreate) -> Optional[dict[str, Any]]:
        return await self._repository.update(metadata_id, data)

    async def delete(self, metadata_id: str) -> bool:
        return await self._repository.delete(metadata_id)