from fastapi import APIRouter, Depends, HTTPException, Query
import logging
import uuid
import json
import time
from typing import Optional, List

from app.models.schemas import ContractFields
from app.models.database import Contract, get_session_local, ExtractedFields
from app.services.llm_service import get_llm_provider
from app.services.webhook_service import WebhookManager
from app.core.config import get_settings
from app.core.logger import logger

router = APIRouter(prefix="/extract", tags=["extract"])
webhook_manager = WebhookManager()


def get_db():
    """Get database session"""
    settings = get_settings()
    SessionLocal = get_session_local(settings.database_url)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ContractFields)
async def extract_fields(
    document_id: str = Query(...),
    db=Depends(get_db)
):
    """
    Extract structured fields from a contract
    
    - **document_id**: ID of the document to extract from
    - Returns: Structured contract fields (parties, dates, terms, etc.)
    """
    settings = get_settings()
    
    try:
        # Get document from database
        contract = db.query(Contract).filter(Contract.id == document_id).first()
        if not contract:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if not contract.raw_text:
            raise HTTPException(status_code=400, detail="Document has no extracted text")
        
        # Get LLM provider
        llm_provider = get_llm_provider(
            settings.llm_provider,
            settings.openai_api_key or settings.anthropic_api_key,
            settings.model_name
        )
        
        # Extract fields
        start_time = time.time()
        extracted_data = await llm_provider.extract_fields(contract.raw_text)
        extraction_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Store extraction in database
        fields_id = str(uuid.uuid4())
        extracted_fields = ExtractedFields(
            id=fields_id,
            contract_id=document_id,
            parties=json.dumps(extracted_data.get("parties", [])),
            effective_date=extracted_data.get("effective_date"),
            term=extracted_data.get("term"),
            governing_law=extracted_data.get("governing_law"),
            payment_terms=extracted_data.get("payment_terms"),
            termination=extracted_data.get("termination"),
            auto_renewal=extracted_data.get("auto_renewal"),
            confidentiality=extracted_data.get("confidentiality"),
            indemnity=extracted_data.get("indemnity"),
            liability_cap=json.dumps(extracted_data.get("liability_cap", {})),
            signatories=json.dumps(extracted_data.get("signatories", [])),
            extraction_time_ms=extraction_time
        )
        db.add(extracted_fields)
        db.commit()
        
        logger.info(f"Extracted fields from document {document_id} in {extraction_time:.2f}ms")
        
        # Emit webhook event
        await webhook_manager.emit_event(
            "extraction_complete",
            document_id,
            {
                "fields_id": fields_id,
                "extraction_time_ms": extraction_time
            }
        )
        
        # Return as response model
        return ContractFields(
            document_id=document_id,
            parties=extracted_data.get("parties", []),
            effective_date=extracted_data.get("effective_date"),
            term=extracted_data.get("term"),
            governing_law=extracted_data.get("governing_law"),
            payment_terms=extracted_data.get("payment_terms"),
            termination=extracted_data.get("termination"),
            auto_renewal=extracted_data.get("auto_renewal"),
            confidentiality=extracted_data.get("confidentiality"),
            indemnity=extracted_data.get("indemnity"),
            liability_cap=extracted_data.get("liability_cap"),
            signatories=extracted_data.get("signatories", []),
            raw_text=contract.raw_text[:1000] if contract.raw_text else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction failed for {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("/fields/{document_id}")
async def get_extracted_fields(
    document_id: str,
    db=Depends(get_db)
):
    """Get previously extracted fields for a document"""
    try:
        extracted = db.query(ExtractedFields).filter(
            ExtractedFields.contract_id == document_id
        ).first()
        
        if not extracted:
            raise HTTPException(status_code=404, detail="Extracted fields not found")
        
        return {
            "document_id": document_id,
            "parties": json.loads(extracted.parties) if extracted.parties else [],
            "effective_date": extracted.effective_date,
            "term": extracted.term,
            "governing_law": extracted.governing_law,
            "payment_terms": extracted.payment_terms,
            "termination": extracted.termination,
            "auto_renewal": extracted.auto_renewal,
            "confidentiality": extracted.confidentiality,
            "indemnity": extracted.indemnity,
            "liability_cap": json.loads(extracted.liability_cap) if extracted.liability_cap else None,
            "signatories": json.loads(extracted.signatories) if extracted.signatories else [],
            "extraction_date": extracted.extraction_date.isoformat(),
            "extraction_time_ms": extracted.extraction_time_ms
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get extracted fields: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve fields")
