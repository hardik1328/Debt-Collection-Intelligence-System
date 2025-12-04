#!/usr/bin/env python
"""Main entry point for the application"""
import uvicorn
import os
from app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
