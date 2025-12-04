from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import logging

from app.core.config import get_settings
from app.models.database import create_tables
from app.api import ingest, extract, ask, audit, admin, webhooks
from app.core.logger import logger

settings = get_settings()

# Create database tables
create_tables(settings.database_url)

# Initialize FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router)
app.include_router(extract.router)
app.include_router(ask.router)
app.include_router(audit.router)
app.include_router(admin.router)
app.include_router(webhooks.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs": "/docs",
        "health": "/admin/healthz"
    }


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Vector Store: {settings.vector_store_type}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info("Shutting down application")


def custom_openapi():
    """Custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
