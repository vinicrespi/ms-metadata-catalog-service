from copy import deepcopy
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.application.use_cases.history_service import HistoryService
from app.application.use_cases.services import MetadataService
from app.application.use_cases.validate_and_update_schema import ValidateAndUpdateSchema
from app.infrastructure.dependencies import (
    get_history_service,
    get_metadata_service,
    get_validate_and_update_schema,
    require_authenticated_user,
)
from app.main import app
from tests.mocks.metadata_create_payload import METADATA_PAYLOAD
from tests.mocks.schema_validation_payload import ADDITIONAL_SCHEMA


class InMemoryMetadataRepository:
    def __init__(self) -> None:
        self.items: dict[str, dict] = {}
        self.next_id = 1

    async def create(self, metadata, change_type, changed_by, details):
        item = metadata.model_dump()
        item["id"] = f"metadata-{self.next_id}"
        self.items[item["id"]] = item
        self.next_id += 1
        return item

    async def get_all(self):
        return list(self.items.values())

    async def get_by_id(self, metadata_id):
        return self.items.get(metadata_id)

    async def update(self, metadata_id, data, changed_by="api", change_type="METADATA_UPDATE", details=None):
        item = self.items.get(metadata_id)
        if item is None:
            return None
        item.update(data.model_dump(exclude_unset=True, exclude_none=True))
        item["updated_at"] = datetime.now(timezone.utc)
        return item

    async def delete(self, metadata_id):
        return self.items.pop(metadata_id, None) is not None


class InMemoryHistoryRepository:
    async def get_by_metadata_id(self, metadata_id):
        return [{"table_id": metadata_id, "version": 3}]


@pytest.fixture
def api_client():
    metadata_repository = InMemoryMetadataRepository()
    history_repository = InMemoryHistoryRepository()
    app.dependency_overrides[get_metadata_service] = lambda: MetadataService(metadata_repository)
    app.dependency_overrides[get_validate_and_update_schema] = lambda: ValidateAndUpdateSchema(
        metadata_repository
    )
    app.dependency_overrides[get_history_service] = lambda: HistoryService(history_repository)
    app.dependency_overrides[require_authenticated_user] = lambda: {"username": "test"}

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_health_is_public(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metadata_crud_flow(api_client: TestClient) -> None:
    created = api_client.post("/metadata", json=METADATA_PAYLOAD)
    assert created.status_code == 201
    metadata_id = created.json()["id"]

    listed = api_client.get("/metadata")
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == metadata_id

    fetched = api_client.get(f"/metadata/{metadata_id}")
    assert fetched.status_code == 200

    update = api_client.put(
        f"/metadata/{metadata_id}",
        json={"owner": "platform"},
    )
    assert update.status_code == 200
    assert update.json()["owner"] == "platform"

    deleted = api_client.delete(f"/metadata/{metadata_id}")
    assert deleted.status_code == 204
    assert api_client.get(f"/metadata/{metadata_id}").status_code == 404


def test_metadata_history_is_scoped_by_metadata_id(api_client: TestClient) -> None:
    response = api_client.get("/metadata/metadata-1/histories")
    assert response.status_code == 200
    assert response.json() == [{"table_id": "metadata-1", "version": 3}]


def test_schema_update_validates_and_increments_version(api_client: TestClient) -> None:
    created = api_client.post("/metadata", json=METADATA_PAYLOAD)
    metadata_id = created.json()["id"]
    new_schema = METADATA_PAYLOAD["current_schema"] + ADDITIONAL_SCHEMA

    response = api_client.put(
        f"/metadata/{metadata_id}",
        json={"current_schema": new_schema},
    )

    assert response.status_code == 200
    assert response.json()["current_version"] == METADATA_PAYLOAD["current_version"] + 1
    assert response.json()["current_schema"] == new_schema


def test_schema_update_rejects_breaking_change(api_client: TestClient) -> None:
    created = api_client.post("/metadata", json=METADATA_PAYLOAD)
    metadata_id = created.json()["id"]

    response = api_client.put(
        f"/metadata/{metadata_id}",
        json={"current_schema": []},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "domain_error"


def test_invalid_metadata_payload_returns_standard_error(api_client: TestClient) -> None:
    payload = deepcopy(METADATA_PAYLOAD)
    payload["legacy_field"] = True
    response = api_client.post("/metadata", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_protected_metadata_requires_authentication() -> None:
    app.dependency_overrides.clear()
    with TestClient(app) as client:
        response = client.get("/metadata")
    assert response.status_code == 401
