from typing import Any, Optional, Protocol

from app.domain.models import MetadataCreate, MetadataUpdate


class MetadataRepositoryPort(Protocol):

    async def create(self, data: MetadataCreate) -> dict[str, Any]:
        ...

    async def get_all(self) -> list[dict[str, Any]]:
        ...

    async def get_by_id(self, metadata_id: str) -> Optional[dict[str, Any]]:
        ...

    async def update(
        self,
        metadata_id: str,
        data: MetadataUpdate,
    ) -> Optional[dict[str, Any]]:
        ...

    async def delete(self, metadata_id: str) -> bool:
        ...