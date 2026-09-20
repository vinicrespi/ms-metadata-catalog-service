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