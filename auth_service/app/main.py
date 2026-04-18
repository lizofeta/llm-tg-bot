from fastapi import FastAPI
from contextlib import asynccontextmanager

from .api.exception_handler import register_exception_handlers
from .api.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App started")
    yield
    print("App stopped")

app = FastAPI(lifespan=lifespan)

register_exception_handlers(app)
app.include_router(api_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
