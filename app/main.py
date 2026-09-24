import logging
from time import perf_counter

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError

from app.adapters.inbound.error_handlers import (
	AuthenticationError,
	DomainError,
	MetadataNotFoundError,
	UserAlreadyExistsError,
	handle_database_exception,
	handle_authentication_exception,
	handle_domain_exception,
	handle_http_exception,
	handle_not_found_exception,
	handle_unexpected_exception,
	handle_validation_exception,
	handle_user_already_exists_exception,
)
from app.adapters.inbound.routers import router
from app.infrastructure.database import lifespan

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Metadata Service", version="0.1.0", lifespan=lifespan)
app.include_router(router)


@app.middleware("http")
async def log_requests(request, call_next):
	started_at = perf_counter()
	response = await call_next(request)
	duration_ms = (perf_counter() - started_at) * 1000
	logger.info(
		"HTTP request method=%s path=%s status=%s duration_ms=%.2f",
		request.method,
		request.url.path,
		response.status_code,
		duration_ms,
	)
	return response

app.add_exception_handler(HTTPException, handle_http_exception)
app.add_exception_handler(RequestValidationError, handle_validation_exception)
app.add_exception_handler(MetadataNotFoundError, handle_not_found_exception)
app.add_exception_handler(AuthenticationError, handle_authentication_exception)
app.add_exception_handler(UserAlreadyExistsError, handle_user_already_exists_exception)
app.add_exception_handler(DomainError, handle_domain_exception)
app.add_exception_handler(PyMongoError, handle_database_exception)
app.add_exception_handler(Exception, handle_unexpected_exception)