"""PDF Ingestion Router"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import os
from pathlib import Path

router = APIRouter()

UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/")
async def ingest_documents(files: List[UploadFile] = File(...)):
    """Upload and ingest PDF documents"""
    try:
        document_ids = []
        documents = []
        
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files allowed")
            
            # Save file
            file_path = UPLOAD_DIR / file.filename
            content = await file.read()
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            document_ids.append(file.filename)
            documents.append({
                "id": file.filename,
                "filename": file.filename,
                "size": len(content)
            })
        
        return {
            "document_ids": document_ids,
            "documents": documents,
            "message": f"Ingested {len(document_ids)} documents"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents(skip: int = 0, limit: int = 10):
    """List ingested documents"""
    try:
        files = list(UPLOAD_DIR.glob("*.pdf"))[skip:skip+limit]
        documents = [
            {
                "id": f.stem,
                "filename": f.name,
                "size": f.stat().st_size
            }
            for f in files
        ]
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get document details"""
    try:
        file_path = UPLOAD_DIR / f"{document_id}.pdf"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {
            "id": document_id,
            "filename": f"{document_id}.pdf",
            "size": file_path.stat().st_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        file_path = UPLOAD_DIR / f"{document_id}.pdf"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path.unlink()
        return {"message": f"Document {document_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
