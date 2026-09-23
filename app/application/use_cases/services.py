import logging
from typing import Any, Optional

from app.application.ports.metadata_port import MetadataPort
from app.domain.models.metadata import Metadata, MetadataUpdate

logger = logging.getLogger(__name__)


class MetadataService:

    def __init__(self, repository: MetadataPort) -> None:
        self._repository = repository

    async def create(
        self,
        metadata: Metadata,
        change_type: str,
        changed_by: str,
        details: Any,
    ) -> dict[str, Any]:
        logger.info(
            "Creating metadata version table_name=%s change_type=%s changed_by=%s",
            metadata.table_name,
            change_type,
            changed_by,
        )
        return await self._repository.create(
            metadata, change_type, changed_by, details
        )

    async def get_all(self) -> list[dict[str, Any]]:
        logger.info("Listing metadata")
        return await self._repository.get_all()

    async def get_by_id(self, metadata_id: str) -> Optional[dict[str, Any]]:
        logger.info("Getting metadata metadata_id=%s", metadata_id)
        return await self._repository.get_by_id(metadata_id)

    async def update(
        self,
        metadata_id: str,
        data: MetadataUpdate,
        changed_by: str = "api",
        change_type: str = "METADATA_UPDATE",
        details: Any = None,
    ) -> Optional[dict[str, Any]]:
        logger.info("Updating metadata metadata_id=%s", metadata_id)
        return await self._repository.update(
            metadata_id, data, changed_by, change_type, details
        )

    async def delete(self, metadata_id: str) -> bool:
        logger.info("Deleting metadata metadata_id=%s", metadata_id)
        return await self._repository.delete(metadata_id)
