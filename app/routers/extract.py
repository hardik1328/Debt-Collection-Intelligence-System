"""Field Extraction Router"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter()


@router.post("/")
async def extract_fields(document_id: str = Query(...)):
    """Extract structured fields from contract"""
    try:
        return {
            "document_id": document_id,
            "fields": {
                "parties": "TBD",
                "governing_law": "TBD",
                "liability_cap": "TBD",
                "payment_terms": "TBD",
                "effective_date": "TBD"
            },
            "message": "Extraction in progress"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fields/{document_id}")
async def get_extracted_fields(document_id: str):
    """Get previously extracted fields"""
    try:
        return {
            "document_id": document_id,
            "fields": {},
            "message": "No extracted fields found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
