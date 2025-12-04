from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from typing import List, Optional
import logging
import uuid
import os
from datetime import datetime
import time

from app.models.schemas import IngestResponse, ContractFields
from app.services.pdf_service import PDFExtractor
from app.models.database import Contract, get_session_local
from app.core.config import get_settings

router = APIRouter(prefix="/ingest", tags=["ingest"])
logger = logging.getLogger(__name__)


def get_db():
    """Get database session"""
    settings = get_settings()
    SessionLocal = get_session_local(settings.database_url)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=IngestResponse)
async def ingest_documents(
    files: List[UploadFile] = File(...),
    db=Depends(get_db)
):
    """
    Ingest PDF documents
    
    - **files**: List of PDF files to ingest
    - Returns: document_ids and metadata for each ingested document
    """
    settings = get_settings()
    document_ids = []
    documents = []
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_dir, exist_ok=True)
    
    for file in files:
        try:
            # Validate file
            if not file.filename:
                continue
            
            if not file.filename.lower().endswith('.pdf'):
                logger.warning(f"Skipping non-PDF file: {file.filename}")
                continue
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Save file
            file_path = os.path.join(settings.upload_dir, f"{doc_id}_{file.filename}")
            
            contents = await file.read()
            file_size = len(contents)
            
            # Check file size
            if file_size > settings.max_file_size:
                logger.error(f"File too large: {file.filename}")
                continue
            
            with open(file_path, "wb") as f:
                f.write(contents)
            
            logger.info(f"Saved file: {file_path}")
            
            # Extract text
            start_time = time.time()
            text_content, page_count = PDFExtractor.extract_text(file_path)
            extraction_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Store in database
            contract = Contract(
                id=doc_id,
                filename=file.filename,
                file_path=file_path,
                raw_text=text_content,
                pages=page_count,
                file_size=file_size,
                upload_date=datetime.utcnow(),
                processed=1,
                processing_time_ms=extraction_time
            )
            db.add(contract)
            db.commit()
            
            document_ids.append(doc_id)
            documents.append({
                "document_id": doc_id,
                "filename": file.filename,
                "pages": page_count,
                "size": file_size,
                "upload_date": contract.upload_date.isoformat(),
                "processing_time_ms": extraction_time
            })
            
            logger.info(f"Ingested document {doc_id}: {file.filename} ({page_count} pages)")
            
        except Exception as e:
            logger.error(f"Failed to ingest file {file.filename}: {str(e)}")
            continue
    
    if not document_ids:
        raise HTTPException(status_code=400, detail="No valid PDF files provided")
    
    return IngestResponse(document_ids=document_ids, documents=documents)


@router.get("/documents", tags=["ingest"])
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    """List ingested documents"""
    try:
        contracts = db.query(Contract).offset(skip).limit(limit).all()
        return [
            {
                "document_id": c.id,
                "filename": c.filename,
                "pages": c.pages,
                "size": c.file_size,
                "upload_date": c.upload_date.isoformat(),
                "processing_time_ms": c.processing_time_ms
            }
            for c in contracts
        ]
    except Exception as e:
        logger.error(f"Failed to list documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list documents")


@router.get("/documents/{document_id}", tags=["ingest"])
async def get_document(document_id: str, db=Depends(get_db)):
    """Get document details"""
    try:
        contract = db.query(Contract).filter(Contract.id == document_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "document_id": contract.id,
            "filename": contract.filename,
            "pages": contract.pages,
            "size": contract.file_size,
            "upload_date": contract.upload_date.isoformat(),
            "processing_time_ms": contract.processing_time_ms,
            "text_preview": contract.raw_text[:500] if contract.raw_text else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document")


@router.delete("/documents/{document_id}", tags=["ingest"])
async def delete_document(document_id: str, db=Depends(get_db)):
    """Delete a document"""
    try:
        contract = db.query(Contract).filter(Contract.id == document_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete file
        if os.path.exists(contract.file_path):
            os.remove(contract.file_path)
        
        # Delete from database
        db.delete(contract)
        db.commit()
        
        logger.info(f"Deleted document {document_id}")
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")
