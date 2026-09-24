from unittest.mock import AsyncMock

import pytest

from app.adapters.inbound.error_handlers import AuthenticationError, UserAlreadyExistsError
from app.application.use_cases.auth_service import AuthService
from app.domain.models.security import LoginRequest, UserCreate
from app.infrastructure.security import get_password_hash


@pytest.mark.asyncio
async def test_auth_service_creates_user() -> None:
    repository = AsyncMock()
    repository.get_by_username.return_value = None
    repository.create_user.return_value = {"id": "user-1", "username": "alice"}
    service = AuthService(repository)

    result = await service.create_user(
        UserCreate(username="alice", password="strong-password")
    )

    assert result["username"] == "alice"
    repository.create_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_service_rejects_duplicate_user() -> None:
    repository = AsyncMock()
    repository.get_by_username.return_value = {"username": "alice"}
    service = AuthService(repository)

    with pytest.raises(UserAlreadyExistsError, match="Username already exists"):
        await service.create_user(
            UserCreate(username="alice", password="strong-password")
        )


@pytest.mark.asyncio
async def test_auth_service_returns_token_for_valid_credentials() -> None:
    repository = AsyncMock()
    repository.get_by_username.return_value = {
        "username": "alice",
        "password_hash": get_password_hash("strong-password"),
    }
    service = AuthService(repository)

    result = await service.authenticate(
        LoginRequest(username="alice", password="strong-password")
    )

    assert result.access_token
    assert result.token_type == "bearer"


@pytest.mark.asyncio
async def test_auth_service_rejects_invalid_credentials() -> None:
    repository = AsyncMock()
    repository.get_by_username.return_value = None
    service = AuthService(repository)

    with pytest.raises(AuthenticationError, match="Invalid credentials"):
        await service.authenticate(
            LoginRequest(username="alice", password="wrong-password")
        )
