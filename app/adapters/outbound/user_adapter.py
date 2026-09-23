from typing import Any, Optional

from pymongo import AsyncMongoClient

from app.application.ports.user_port import UserPort
from app.domain.models.security import UserCreate, UserResponse
from app.infrastructure.security import get_password_hash


class MongoUserAdapter(UserPort):
    def __init__(self, client: AsyncMongoClient, database_name: str) -> None:
        self._collection = client[database_name]["users"]

    async def initialize(self) -> None:
        await self._collection.create_index("username", unique=True)

    async def create_user(self, data: UserCreate) -> UserResponse:
        document = {
            "username": data.username,
            "password_hash": get_password_hash(data.password),
        }
        result = await self._collection.insert_one(document)
        return UserResponse(id=str(result.inserted_id), username=data.username)

    async def get_by_username(self, username: str) -> Optional[dict[str, Any]]:
        return await self._collection.find_one({"username": username})