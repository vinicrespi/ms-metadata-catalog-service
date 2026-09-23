from unittest.mock import AsyncMock
from types import SimpleNamespace

import pytest

from app.application.use_cases.services import MetadataService
from app.domain.models.metadata import MetadataUpdate


@pytest.mark.asyncio
async def test_metadata_service_delegates_create() -> None:
    repository = AsyncMock()
    expected = {"id": "metadata-1"}
    repository.create.return_value = expected
    service = MetadataService(repository)
    metadata = SimpleNamespace(table_name="orders")

    result = await service.create(metadata, "INITIAL_CREATION", "pipeline", {})

    assert result == expected
    repository.create.assert_awaited_once_with(
        metadata, "INITIAL_CREATION", "pipeline", {}
    )


@pytest.mark.asyncio
async def test_metadata_service_update_passes_history_context() -> None:
    repository = AsyncMock()
    repository.update.return_value = {"id": "metadata-1", "current_version": 2}
    service = MetadataService(repository)
    update = MetadataUpdate(owner="platform")

    result = await service.update(
        "metadata-1", update, "operator", "METADATA_UPDATE", {"reason": "owner"}
    )

    assert result["current_version"] == 2
    repository.update.assert_awaited_once_with(
        "metadata-1", update, "operator", "METADATA_UPDATE", {"reason": "owner"}
    )


@pytest.mark.asyncio
async def test_metadata_service_delegates_queries_and_delete() -> None:
    repository = AsyncMock()
    repository.get_all.return_value = [{"id": "metadata-1"}]
    repository.get_by_id.return_value = {"id": "metadata-1"}
    repository.delete.return_value = True
    service = MetadataService(repository)

    assert await service.get_all() == [{"id": "metadata-1"}]
    assert await service.get_by_id("metadata-1") == {"id": "metadata-1"}
    assert await service.delete("metadata-1") is True
