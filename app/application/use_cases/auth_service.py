from datetime import timedelta

from app.adapters.inbound.error_handlers import AuthenticationError, UserAlreadyExistsError
from app.application.ports.user_port import UserPort
from app.domain.models.security import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.infrastructure.security import create_access_token, verify_password


class AuthService:
    def __init__(self, repository: UserPort) -> None:
        self._repository = repository

    async def create_user(self, data: UserCreate) -> UserResponse:
        existing = await self._repository.get_by_username(data.username)
        if existing is not None:
            raise UserAlreadyExistsError("Username already exists")
        return await self._repository.create_user(data)

    async def authenticate(self, data: LoginRequest) -> TokenResponse:
        user = await self._repository.get_by_username(data.username)
        if user is None:
            raise AuthenticationError("Invalid credentials")

        valid, _ = verify_password(data.password, user["password_hash"])
        if not valid:
            raise AuthenticationError("Invalid credentials")

        token = create_access_token(user["username"], timedelta(minutes=30))
        return TokenResponse(access_token=token)