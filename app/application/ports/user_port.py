from typing import Any, Optional, Protocol

from app.domain.models.security import UserCreate, UserResponse


class UserPort(Protocol):
    async def create_user(self, data: UserCreate) -> UserResponse:
        ...

    async def get_by_username(self, username: str) -> Optional[dict[str, Any]]:
        ...
