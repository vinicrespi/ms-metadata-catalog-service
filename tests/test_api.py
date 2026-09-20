from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.application.use_cases.services import MetadataService
from app.infrastructure.database import get_metadata_service
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


client = TestClient(app)

def test_metadata_health_endpoint() -> None:
        response = client.get("/health")
        assert response.status_code == 200

def test_metadata_create_endpoint() -> None:
    repository = InMemoryMetadataRepository()
    app.dependency_overrides[get_metadata_service] = lambda: MetadataService(repository)

    try:
        created = client.post("/metadata", json=METADATA_CREATE_PAYLOAD)

        assert created.status_code == 201
    finally:
        app.dependency_overrides.clear()