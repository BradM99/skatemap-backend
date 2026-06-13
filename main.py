from fastapi import FastAPI
from config import settings

from api import spots
from database.db import create_db

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="FastAPI backend for Skatemap",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.include_router(spots.router)

@app.on_event("startup")
def startup():
    create_db()

@app.get("/")
def root():
    return {"message": "API is running"}
