from fastapi import APIRouter, Depends, HTTPException, Query
import logging
import uuid
import json
import time
from typing import Optional, List

from app.models.schemas import AuditRequest, AuditResponse, RiskFinding, SeverityEnum, CitationSpan
from app.models.database import Contract, AuditFinding, get_session_local
from app.services.llm_service import get_llm_provider
from app.services.webhook_service import WebhookManager
from app.core.config import get_settings
from app.core.logger import logger

router = APIRouter(prefix="/audit", tags=["audit"])
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


@router.post("", response_model=AuditResponse)
async def audit_contract(
    document_id: str = Query(...),
    db=Depends(get_db)
):
    """
    Run risk audit on a contract
    
    - **document_id**: ID of the document to audit
    - Returns: List of risky clauses with severity and recommendations
    """
    settings = get_settings()
    
    try:
        # Get document
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
        
        # Detect risks
        start_time = time.time()
        risks_data = await llm_provider.detect_risks(contract.raw_text)
        audit_time = (time.time() - start_time) * 1000  # Convert to ms
        
        findings = []
        for risk in risks_data:
            finding = RiskFinding(
                clause_type=risk.get("clause_type", "Unknown"),
                severity=SeverityEnum(risk.get("severity", "low")),
                description=risk.get("description", ""),
                evidence_spans=[
                    CitationSpan(
                        document_id=document_id,
                        page=1,
                        start_char=0,
                        end_char=200,
                        text=risk.get("evidence", "")[:200]
                    )
                ],
                recommendation=risk.get("recommendation")
            )
            findings.append(finding)
            
            # Store in database
            audit_finding = AuditFinding(
                id=str(uuid.uuid4()),
                contract_id=document_id,
                clause_type=risk.get("clause_type"),
                severity=risk.get("severity"),
                description=risk.get("description"),
                evidence=json.dumps({"text": risk.get("evidence")}),
                recommendation=risk.get("recommendation")
            )
            db.add(audit_finding)
        
        db.commit()
        
        # Generate summary
        critical_count = sum(1 for f in findings if f.severity == SeverityEnum.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == SeverityEnum.HIGH)
        medium_count = sum(1 for f in findings if f.severity == SeverityEnum.MEDIUM)
        
        summary = f"Found {len(findings)} risk findings: {critical_count} critical, {high_count} high, {medium_count} medium"
        
        logger.info(f"Completed audit for {document_id} in {audit_time:.2f}ms: {summary}")
        
        # Emit webhook event
        await webhook_manager.emit_event(
            "audit_complete",
            document_id,
            {
                "findings_count": len(findings),
                "critical_count": critical_count,
                "high_count": high_count,
                "audit_time_ms": audit_time
            }
        )
        
        return AuditResponse(
            document_id=document_id,
            findings=findings,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audit failed for {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")


@router.get("/findings/{document_id}", tags=["audit"])
async def get_audit_findings(
    document_id: str,
    severity: Optional[str] = Query(None),
    db=Depends(get_db)
):
    """Get audit findings for a document"""
    try:
        query = db.query(AuditFinding).filter(AuditFinding.contract_id == document_id)
        
        if severity:
            query = query.filter(AuditFinding.severity == severity)
        
        findings = query.all()
        
        return [
            {
                "id": f.id,
                "clause_type": f.clause_type,
                "severity": f.severity,
                "description": f.description,
                "evidence": json.loads(f.evidence) if f.evidence else {},
                "recommendation": f.recommendation,
                "audit_date": f.audit_date.isoformat()
            }
            for f in findings
        ]
    except Exception as e:
        logger.error(f"Failed to get audit findings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve findings")


@router.get("/summary/{document_id}", tags=["audit"])
async def get_audit_summary(
    document_id: str,
    db=Depends(get_db)
):
    """Get audit summary for a document"""
    try:
        findings = db.query(AuditFinding).filter(AuditFinding.contract_id == document_id).all()
        
        if not findings:
            return {
                "document_id": document_id,
                "total_findings": 0,
                "by_severity": {},
                "risk_level": "LOW"
            }
        
        by_severity = {}
        for f in findings:
            severity = f.severity
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # Determine overall risk level
        if by_severity.get("critical", 0) > 0:
            risk_level = "CRITICAL"
        elif by_severity.get("high", 0) > 0:
            risk_level = "HIGH"
        elif by_severity.get("medium", 0) > 0:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return {
            "document_id": document_id,
            "total_findings": len(findings),
            "by_severity": by_severity,
            "risk_level": risk_level
        }
    except Exception as e:
        logger.error(f"Failed to get audit summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve summary")
