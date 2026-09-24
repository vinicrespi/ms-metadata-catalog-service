from typing import Any, Optional

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.adapters.inbound.error_handlers import AuthenticationError
from app.application.ports.history_port import HistoryPort
from app.application.ports.metadata_port import MetadataPort
from app.application.use_cases.history_service import HistoryService
from app.application.use_cases.auth_service import AuthService
from app.application.use_cases.services import MetadataService
from app.application.use_cases.validate_and_update_schema import ValidateAndUpdateSchema
from app.infrastructure.security import ALGORITHM, settings

bearer_scheme = HTTPBearer(auto_error=False)


def get_metadata_service(request: Request) -> MetadataService:
    repository: MetadataPort = request.app.state.metadata_repository
    return MetadataService(repository)


def get_metadata_repository(request: Request) -> MetadataPort:
    return request.app.state.metadata_repository


def get_validate_and_update_schema(
    repository: MetadataPort = Depends(get_metadata_repository),
) -> ValidateAndUpdateSchema:
    return ValidateAndUpdateSchema(repository)


def get_history_service(request: Request) -> HistoryService:
    repository: HistoryPort = request.app.state.history_repository
    return HistoryService(repository)


def get_auth_service(request: Request) -> AuthService:
    return AuthService(request.app.state.user_repository)


async def require_authenticated_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("Authentication required")

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        username = payload.get("sub")
        if not isinstance(username, str) or not username:
            raise ValueError("Token subject is missing")
    except (jwt.PyJWTError, ValueError):
        raise AuthenticationError("Invalid or expired token")

    user = await request.app.state.user_repository.get_by_username(username)
    if user is None:
        raise AuthenticationError("User is no longer active")
    return user
