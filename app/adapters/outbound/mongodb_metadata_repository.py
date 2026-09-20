from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from pymongo import AsyncMongoClient

from app.domain.models import MetadataCreate


class MongoMetadataRepository:

    def __init__(self, client: AsyncMongoClient, database_name: str) -> None:
        self._collection = client[database_name]["metadata"]

    @staticmethod
    def _to_response(document: dict[str, Any]) -> dict[str, Any]:
        document["id"] = str(document.pop("_id"))
        return document


    async def create(self, data: MetadataCreate) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        metadata = data.model_dump() | {"created_at": now, "updated_at": now}
        result = await self._collection.insert_one(metadata)
        metadata["_id"] = result.inserted_id
        return self._to_response(metadata)
