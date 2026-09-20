from datetime import datetime, timezone

import pytest

from fastapi.testclient import TestClient

from app.application.use_cases.services import MetadataService
from app.infrastructure.dependencies import get_metadata_service
from app.main import app
from tests.mocks.metadata_create_payload import METADATA_CREATE_PAYLOAD


class InMemoryMetadataRepository:
    def __init__(self) -> None:
        self.items: dict[str, dict] = {}
        self.next_id = 1

    async def create(self, data):
        now = datetime.now(timezone.utc)
        metadata = {
            "id": str(self.next_id),
            **data.model_dump(),
            "created_at": now,
            "updated_at": now,
        }
        self.items[metadata["id"]] = metadata
        self.next_id += 1
        return metadata

    async def get_all(self):
        return list(self.items.values())

    async def get_by_id(self, metadata_id):
        return self.items.get(metadata_id)

    async def update(self, metadata_id, data):
        metadata = self.items.get(metadata_id)
        if metadata is None:
            return None
        metadata.update(data.model_dump())
        metadata["updated_at"] = datetime.now(timezone.utc)
        return metadata

    async def delete(self, metadata_id):
        return self.items.pop(metadata_id, None) is not None


@pytest.fixture
def api_client():
    repository = InMemoryMetadataRepository()
    app.dependency_overrides[get_metadata_service] = lambda: MetadataService(repository)

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


def test_metadata_health_endpoint(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200


def test_metadata_create_endpoint(api_client: TestClient) -> None:
    created = api_client.post("/metadata", json=METADATA_CREATE_PAYLOAD)

    assert created.status_code == 201


def test_metadata_get_all_endpoint(api_client: TestClient) -> None:
    api_client.post("/metadata", json=METADATA_CREATE_PAYLOAD)

    response = api_client.get("/metadata")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "payments"


def test_metadata_get_by_id_endpoint(api_client: TestClient) -> None:
    created = api_client.post("/metadata", json=METADATA_CREATE_PAYLOAD)
    metadata_id = created.json()["id"]

    response = api_client.get(f"/metadata/{metadata_id}")

    assert response.status_code == 200
    assert response.json()["id"] == metadata_id


def test_metadata_get_by_id_returns_not_found(api_client: TestClient) -> None:
    response = api_client.get("/metadata/nonexistent")

    assert response.status_code == 404
    assert response.json() == {"detail": "Metadata not found"}


def test_metadata_update_endpoint(api_client: TestClient) -> None:
    created = api_client.post("/metadata", json=METADATA_CREATE_PAYLOAD)
    metadata_id = created.json()["id"]
    updated_payload = {**METADATA_CREATE_PAYLOAD, "owner": "platform"}

    response = api_client.put(f"/metadata/{metadata_id}", json=updated_payload)

    assert response.status_code == 200
    assert response.json()["owner"] == "platform"


def test_metadata_update_returns_not_found(api_client: TestClient) -> None:
    response = api_client.put("/metadata/missing", json=METADATA_CREATE_PAYLOAD)

    assert response.status_code == 404


def test_metadata_delete_endpoint(api_client: TestClient) -> None:
    created = api_client.post("/metadata", json=METADATA_CREATE_PAYLOAD)
    metadata_id = created.json()["id"]

    response = api_client.delete(f"/metadata/{metadata_id}")

    assert response.status_code == 204
    assert api_client.get(f"/metadata/{metadata_id}").status_code == 404


def test_metadata_delete_returns_not_found(api_client: TestClient) -> None:
    response = api_client.delete("/metadata/missing")

    assert response.status_code == 404
