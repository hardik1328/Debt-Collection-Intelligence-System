"""FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import os

# Create app instance
app = FastAPI(
    title="Contract Intelligence API",
    description="API for intelligent contract analysis using LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Contract Intelligence API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "http://localhost:8000/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


# Import and register routers
try:
    from app.routers import ingest, extract, ask, audit, webhook, admin
    
    app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
    app.include_router(extract.router, prefix="/extract", tags=["extract"])
    app.include_router(ask.router, prefix="/ask", tags=["ask"])
    app.include_router(audit.router, prefix="/audit", tags=["audit"])
    app.include_router(webhook.router, prefix="/webhook", tags=["webhook"])
    app.include_router(admin.router, prefix="/admin", tags=["admin"])
    
except ImportError as e:
    print(f"Warning: Could not import routers: {e}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )


def custom_openapi():
    """Custom OpenAPI schema with better documentation"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Contract Intelligence API",
        version="1.0.0",
        description="API for intelligent contract analysis using LLMs",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn
    from app.core.config import get_settings
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
