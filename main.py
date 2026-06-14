from contextlib import asynccontextmanager
from fastapi import FastAPI
from config import settings
from database.db import create_db
from api import spots

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI backend for Skatemap",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

app.include_router(spots.router)

@app.get("/")
def root():
    return {"message": "API is running"}
