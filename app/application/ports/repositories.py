from typing import Any, Protocol

from app.domain.models import MetadataCreate


class MetadataRepositoryPort(Protocol):

    async def create(self, data: MetadataCreate) -> dict[str, Any]:
        ...