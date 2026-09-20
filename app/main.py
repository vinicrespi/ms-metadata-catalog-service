from fastapi import FastAPI

from app.adapters.inbound.controllers import router

app = FastAPI(title="Metadata Catalog Service", version="0.1.0")
app.include_router(router)