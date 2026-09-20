from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from pymongo import AsyncMongoClient

from app.domain.models import MetadataCreate, MetadataUpdate


class MongoMetadataRepository:

    def __init__(self, client: AsyncMongoClient, database_name: str) -> None:
        self._collection = client[database_name]["metadata"]

    @staticmethod
    def _to_response(metadata: dict[str, Any]) -> dict[str, Any]:
        metadata["id"] = str(metadata.pop("_id"))
        return metadata
    
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

    async def update(self, metadata_id: str, data: MetadataUpdate) -> Optional[dict[str, Any]]:
        object_id = self._object_id(metadata_id)
        if object_id is None:
            return None
        values = data.model_dump(exclude_unset=True)
        values["updated_at"] = datetime.now(timezone.utc)
        metadata = await self._collection.find_one_and_update(
            {"_id": object_id}, {"$set": values}, return_document=True
        )
        return self._to_response(metadata) if metadata else None

    async def delete(self, metadata_id: str) -> bool:
        object_id = self._object_id(metadata_id)
        if object_id is None:
            return False
        result = await self._collection.delete_one({"_id": object_id})
        return result.deleted_count == 1