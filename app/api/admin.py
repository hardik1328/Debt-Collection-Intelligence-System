from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
import os
import psutil
import logging

from app.models.schemas import HealthResponse, MetricsResponse
from app.models.database import Contract, QueryLog, AuditFinding, get_session_local
from app.core.config import get_settings
from app.core.logger import logger

router = APIRouter(prefix="/admin", tags=["admin"])
start_time = datetime.utcnow()


def get_db():
    """Get database session"""
    settings = get_settings()
    SessionLocal = get_session_local(settings.database_url)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/healthz", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(db=Depends(get_db)):
    """Get system metrics"""
    try:
        # Database counts
        documents_count = db.query(Contract).count()
        queries_count = db.query(QueryLog).count()
        audits_count = db.query(AuditFinding).count()
        
        # Calculate average times
        query_logs = db.query(QueryLog).all()
        avg_qa_time = sum(q.query_time_ms for q in query_logs) / len(query_logs) if query_logs else 0
        
        contracts = db.query(Contract).all()
        avg_extraction_time = sum(c.processing_time_ms for c in contracts) / len(contracts) if contracts else 0
        
        # Uptime
        uptime = (datetime.utcnow() - start_time).total_seconds()
        
        return MetricsResponse(
            documents_ingested=documents_count,
            total_queries=queries_count,
            total_audit_runs=audits_count,
            uptime_seconds=uptime,
            average_extraction_time_ms=avg_extraction_time,
            average_qa_time_ms=avg_qa_time
        )
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@router.get("/status")
async def get_status(db=Depends(get_db)):
    """Get detailed system status"""
    try:
        process = psutil.Process(os.getpid())
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - start_time).total_seconds(),
            "system": {
                "memory_percent": process.memory_percent(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "num_threads": process.num_threads()
            },
            "database": {
                "documents": db.query(Contract).count(),
                "queries": db.query(QueryLog).count(),
                "audit_findings": db.query(AuditFinding).count()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve status")


@router.post("/reset")
async def reset_system(db=Depends(get_db)):
    """Reset system (for development only)"""
    try:
        # Delete all records
        db.query(QueryLog).delete()
        db.query(AuditFinding).delete()
        db.query(Contract).delete()
        db.commit()
        
        logger.warning("System reset: all data cleared")
        return {"message": "System reset successfully"}
    except Exception as e:
        logger.error(f"Reset failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Reset failed")
