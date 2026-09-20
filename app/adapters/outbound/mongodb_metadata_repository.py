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
    
    @staticmethod
    def _object_id(metadata_id: str) -> Optional[ObjectId]:
        return ObjectId(metadata_id) if ObjectId.is_valid(metadata_id) else None

    async def create(self, data: MetadataCreate) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        metadata = data.model_dump() | {"created_at": now, "updated_at": now}
        result = await self._collection.insert_one(metadata)
        metadata["_id"] = result.inserted_id
        return self._to_response(metadata)

    async def get_all(self) -> list[dict[str, Any]]:
        metadatas = await self._collection.find().sort("created_at", -1).to_list()
        return [self._to_response(metadata) for metadata in metadatas]

    async def get_by_id(self, metadata_id: str) -> Optional[dict[str, Any]]:
        object_id = self._object_id(metadata_id)
        if object_id is None:
            return None
        metadata = await self._collection.find_one({"_id": object_id})
        return self._to_response(metadata) if metadata else None