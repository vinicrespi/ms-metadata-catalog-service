from fastapi import FastAPI

from app.adapters.inbound.controllers import router
from app.infrastructure.database import lifespan

app = FastAPI(title="Metadata Catalog Service", version="0.1.0", lifespan=lifespan)
app.include_router(router)