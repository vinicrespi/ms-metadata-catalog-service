from typing import Any, Optional, Protocol

from app.domain.models.metadata import Metadata, MetadataUpdate


class MetadataPort(Protocol):
    async def create(
        self,
        metadata: Metadata,
        change_type: str,
        changed_by: str,
        details: Any,
    ) -> dict[str, Any]:
        ...

    async def get_all(self) -> list[dict[str, Any]]:
        ...

    async def get_by_id(self, metadata_id: str) -> Optional[dict[str, Any]]:
        ...

    async def update(
        self,
        metadata_id: str,
        data: MetadataUpdate,
        changed_by: str = "api",
        change_type: str = "METADATA_UPDATE",
        details: Any = None,
    ) -> Optional[dict[str, Any]]:
        ...

    async def delete(self, metadata_id: str) -> bool:
        ...
