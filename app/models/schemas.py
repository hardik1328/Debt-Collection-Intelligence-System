from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SeverityEnum(str, Enum):
    """Risk severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DocumentMetadata(BaseModel):
    """Document metadata"""
    filename: str
    size: int
    upload_date: datetime
    pages: int


class IngestRequest(BaseModel):
    """Ingest request - for multiple files"""
    pass  # Files handled via multipart form-data


class IngestResponse(BaseModel):
    """Ingest response"""
    document_ids: List[str]
    documents: List[Dict[str, Any]]


class PartyInfo(BaseModel):
    """Party information"""
    name: str
    title: Optional[str] = None


class SignatoryInfo(BaseModel):
    """Signatory information"""
    name: str
    title: Optional[str] = None


class ContractFields(BaseModel):
    """Extracted contract fields"""
    document_id: str
    parties: List[str] = Field(default_factory=list)
    effective_date: Optional[str] = None
    term: Optional[str] = None
    governing_law: Optional[str] = None
    payment_terms: Optional[str] = None
    termination: Optional[str] = None
    auto_renewal: Optional[str] = None
    confidentiality: Optional[str] = None
    indemnity: Optional[str] = None
    liability_cap: Optional[Dict[str, Any]] = None  # {amount, currency}
    signatories: List[SignatoryInfo] = Field(default_factory=list)
    raw_text: Optional[str] = None


class CitationSpan(BaseModel):
    """Citation reference"""
    document_id: str
    page: int
    start_char: int
    end_char: int
    text: str


class AskRequest(BaseModel):
    """Question answering request"""
    question: str
    document_ids: Optional[List[str]] = None
    top_k: int = 5


class AskResponse(BaseModel):
    """Question answering response"""
    question: str
    answer: str
    citations: List[CitationSpan]


class AskStreamRequest(BaseModel):
    """Streaming question request"""
    question: str
    document_ids: Optional[List[str]] = None
    top_k: int = 5


class RiskFinding(BaseModel):
    """Risk audit finding"""
    clause_type: str
    severity: SeverityEnum
    description: str
    evidence_spans: List[CitationSpan]
    recommendation: Optional[str] = None


class AuditRequest(BaseModel):
    """Audit request"""
    document_id: str


class AuditResponse(BaseModel):
    """Audit response"""
    document_id: str
    findings: List[RiskFinding]
    summary: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str


class MetricsResponse(BaseModel):
    """Metrics response"""
    documents_ingested: int
    total_queries: int
    total_audit_runs: int
    uptime_seconds: float
    average_extraction_time_ms: float
    average_qa_time_ms: float


class WebhookPayload(BaseModel):
    """Webhook event payload"""
    event_type: str
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime


class WebhookRegistration(BaseModel):
    """Webhook registration"""
    url: str
    events: List[str] = Field(default_factory=lambda: ["extraction_complete", "audit_complete"])
