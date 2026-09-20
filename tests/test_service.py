from unittest.mock import AsyncMock

import pytest

from app.domain.models import MetadataCreate
from app.application.use_cases.services import MetadataService
from tests.mocks.metadata_create_payload import METADATA_CREATE_PAYLOAD


@pytest.mark.asyncio
async def test_service_delegates_metadata_creation_to_repository() -> None:
    repository = AsyncMock()
    expected = {"id": "1", "name": "payments"}
    repository.create.return_value = expected
    service = MetadataService(repository)
    data = MetadataCreate(**METADATA_CREATE_PAYLOAD)

    result = await service.create(data)

    assert result == expected
    repository.create.assert_awaited_once_with(data)


@pytest.mark.asyncio
async def test_service_delegates_get_all_to_repository() -> None:
    repository = AsyncMock()
    expected = [{"id": "1", "name": "payments"}]
    repository.get_all.return_value = expected
    service = MetadataService(repository)

    result = await service.get_all()

    assert result == expected
    repository.get_all.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_service_returns_metadata_by_id() -> None:
    repository = AsyncMock()
    expected = {"id": "1", "name": "payments"}
    repository.get_by_id.return_value = expected
    service = MetadataService(repository)

    result = await service.get_by_id("1")

    assert result == expected
    repository.get_by_id.assert_awaited_once_with("1")


@pytest.mark.asyncio
async def test_service_returns_none_when_metadata_does_not_exist() -> None:
    repository = AsyncMock()
    repository.get_by_id.return_value = None
    service = MetadataService(repository)

    result = await service.get_by_id("missing")

    assert result is None
    repository.get_by_id.assert_awaited_once_with("missing")


@pytest.mark.asyncio
async def test_service_delegates_update_to_repository() -> None:
    repository = AsyncMock()
    expected = {"id": "1", "name": "payments", "owner": "platform"}
    repository.update.return_value = expected
    service = MetadataService(repository)
    data = MetadataCreate(**{**METADATA_CREATE_PAYLOAD, "owner": "platform"})

    result = await service.update("1", data)

    assert result == expected
    repository.update.assert_awaited_once_with("1", data)


@pytest.mark.asyncio
async def test_service_delegates_delete_to_repository() -> None:
    repository = AsyncMock()
    repository.delete.return_value = True
    service = MetadataService(repository)

    result = await service.delete("1")

    assert result is True
    repository.delete.assert_awaited_once_with("1")