import logging
from typing import Any

from app.application.ports.history_port import HistoryPort

logger = logging.getLogger(__name__)


class HistoryService:
    def __init__(self, repository: HistoryPort) -> None:
        self._repository = repository

    async def get_by_metadata_id(self, metadata_id: str) -> list[dict[str, Any]]:
        logger.info("Listing metadata history metadata_id=%s", metadata_id)
        return await self._repository.get_by_metadata_id(metadata_id)
