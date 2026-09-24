import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.errors import (
    ConnectionFailure,
    DuplicateKeyError,
    OperationFailure,
    PyMongoError,
    ServerSelectionTimeoutError,
)

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Base class for domain errors."""


class MetadataNotFoundError(DomainError):
    """Raised when a metadata entry is not found."""


class AuthenticationError(DomainError):
    """Raised when authentication fails."""


class UserAlreadyExistsError(DomainError):
    """Raised when a username is already registered."""


def _error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    error: dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        error["details"] = details
    return JSONResponse(status_code=status_code, content={"error": error})


async def handle_http_exception(
    request: Request, exception: HTTPException
) -> JSONResponse:
    logger.error(
        "HTTP error method=%s path=%s status=%s",
        request.method,
        request.url.path,
        exception.status_code,
    )
    return _error_response(
        exception.status_code,
        "http_error",
        str(exception.detail),
        getattr(exception, "headers", None),
    )


async def handle_validation_exception(
    request: Request, exception: RequestValidationError
) -> JSONResponse:
    logger.error(
        "Validation error method=%s path=%s errors=%d",
        request.method,
        request.url.path,
        len(exception.errors()),
    )
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "validation_error",
        "Request validation failed",
        jsonable_encoder(exception.errors()),
    )


async def handle_not_found_exception(
    request: Request, exception: MetadataNotFoundError
) -> JSONResponse:
    logger.error("Metadata not found method=%s path=%s", request.method, request.url.path)
    return _error_response(status.HTTP_404_NOT_FOUND, "metadata_not_found", str(exception) or "Metadata not found")


async def handle_domain_exception(
    request: Request, exception: DomainError
) -> JSONResponse:
    logger.warning("Domain error method=%s path=%s", request.method, request.url.path)
    return _error_response(status.HTTP_400_BAD_REQUEST, "domain_error", str(exception) or "Domain error")


async def handle_authentication_exception(
    request: Request, exception: AuthenticationError
) -> JSONResponse:
    logger.warning("Authentication failed method=%s path=%s", request.method, request.url.path)
    response = _error_response(status.HTTP_401_UNAUTHORIZED, "authentication_error", str(exception) or "Authentication failed")
    response.headers["WWW-Authenticate"] = "Bearer"
    return response


async def handle_user_already_exists_exception(
    request: Request, exception: UserAlreadyExistsError
) -> JSONResponse:
    logger.warning("Username already exists method=%s path=%s", request.method, request.url.path)
    return _error_response(status.HTTP_409_CONFLICT, "user_already_exists", str(exception) or "Username already exists")


async def handle_database_exception(
    request: Request, exception: PyMongoError
) -> JSONResponse:
    if isinstance(exception, DuplicateKeyError):
        logger.warning("Duplicate resource method=%s path=%s", request.method, request.url.path)
        return _error_response(status.HTTP_409_CONFLICT, "duplicate_resource", "Metadata already exists")

    if isinstance(
        exception, (ConnectionFailure, ServerSelectionTimeoutError, OperationFailure)
    ):
        logger.exception("Database operation failed", exc_info=exception)
        return _error_response(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "database_unavailable",
            "The metadata database is unavailable",
        )

    logger.exception("Database error", exc_info=exception)
    return _error_response(status.HTTP_503_SERVICE_UNAVAILABLE, "database_error", "The metadata database request failed")


async def handle_unexpected_exception(
    request: Request, exception: Exception
) -> JSONResponse:
    logger.exception("Unhandled application error", exc_info=exception)
    return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", "An unexpected error occurred")

async def handle_unexpected_exception(
    request: Request, exception: Exception
) -> JSONResponse:
    logger.exception("Unhandled application error", exc_info=exception)
    return _error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", "An unexpected error occurred")
