# API Specification

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication required. In production, add JWT/OAuth2.

---

## Endpoints

### 1. Ingestion API

#### POST /ingest
Upload PDF documents for processing.

**Request:**
```
Content-Type: multipart/form-data
```

**Parameters:**
- `files` (required): List of PDF files to upload

**Response:**
```json
{
  "document_ids": ["uuid-1", "uuid-2"],
  "documents": [
    {
      "document_id": "uuid-1",
      "filename": "contract.pdf",
      "pages": 10,
      "size": 512000,
      "upload_date": "2025-01-15T10:00:00Z",
      "processing_time_ms": 245
    }
  ]
}
```

**Status Codes:**
- 200: Success
- 400: Invalid file format
- 413: File too large

---

#### GET /ingest/documents
List all ingested documents.

**Parameters:**
- `skip` (optional): Number of documents to skip (default: 0)
- `limit` (optional): Maximum documents to return (default: 10)

**Response:**
```json
[
  {
    "document_id": "uuid-1",
    "filename": "contract.pdf",
    "pages": 10,
    "size": 512000,
    "upload_date": "2025-01-15T10:00:00Z",
    "processing_time_ms": 245
  }
]
```

---

#### GET /ingest/documents/{document_id}
Get details of a specific document.

**Response:**
```json
{
  "document_id": "uuid-1",
  "filename": "contract.pdf",
  "pages": 10,
  "size": 512000,
  "upload_date": "2025-01-15T10:00:00Z",
  "processing_time_ms": 245,
  "text_preview": "This Agreement is entered into..."
}
```

---

#### DELETE /ingest/documents/{document_id}
Delete a document and its related data.

**Response:**
```json
{
  "message": "Document deleted successfully"
}
```

---

### 2. Extraction API

#### POST /extract
Extract structured fields from a contract.

**Parameters:**
- `document_id` (required): Document to extract from

**Response:**
```json
{
  "document_id": "uuid-1",
  "parties": ["Company A", "Company B"],
  "effective_date": "2025-01-01",
  "term": "12 months",
  "governing_law": "New York",
  "payment_terms": "Net 30",
  "termination": "Either party may terminate with 30 days notice",
  "auto_renewal": "Automatically renews for 12 months",
  "confidentiality": "Mutual NDA",
  "indemnity": "Each party indemnifies the other",
  "liability_cap": {
    "amount": "100000",
    "currency": "$"
  },
  "signatories": [
    {
      "name": "John Doe",
      "title": "CEO"
    }
  ],
  "raw_text": "..."
}
```

---

#### GET /extract/fields/{document_id}
Get previously extracted fields.

**Response:**
```json
{
  "document_id": "uuid-1",
  "parties": ["Company A", "Company B"],
  "effective_date": "2025-01-01",
  "term": "12 months",
  "governing_law": "New York",
  "payment_terms": "Net 30",
  "termination": "...",
  "auto_renewal": "...",
  "confidentiality": "...",
  "indemnity": "...",
  "liability_cap": { "amount": "100000", "currency": "$" },
  "signatories": [],
  "extraction_date": "2025-01-15T10:05:00Z",
  "extraction_time_ms": 245
}
```

---

### 3. Question Answering API

#### POST /ask
Answer questions about contracts.

**Request:**
```json
{
  "question": "What is the payment term?",
  "document_ids": ["uuid-1"],
  "top_k": 5
}
```

**Response:**
```json
{
  "question": "What is the payment term?",
  "answer": "The payment term is Net 30, meaning payments are due within 30 days of invoice.",
  "citations": [
    {
      "document_id": "uuid-1",
      "page": 2,
      "start_char": 150,
      "end_char": 200,
      "text": "Payment shall be made within thirty (30) days..."
    }
  ]
}
```

---

#### GET /ask/stream
Stream answer tokens using Server-Sent Events.

**Parameters:**
- `question` (required): Question to answer
- `document_ids` (optional): Comma-separated document IDs
- `top_k` (optional): Number of passages to retrieve

**Response:** SSE stream
```
data: {"chunk": "The"}
data: {"chunk": " payment"}
data: {"chunk": " term"}
data: [DONE]
```

---

#### GET /ask/queries
Get query history.

**Parameters:**
- `skip` (optional): Number of queries to skip
- `limit` (optional): Maximum queries to return

**Response:**
```json
[
  {
    "id": "query-1",
    "question": "What is the payment term?",
    "answer": "...",
    "document_ids": ["uuid-1"],
    "query_time_ms": 450,
    "query_date": "2025-01-15T10:30:00Z"
  }
]
```

---

### 4. Audit API

#### POST /audit
Run risk audit on a contract.

**Parameters:**
- `document_id` (required): Document to audit

**Response:**
```json
{
  "document_id": "uuid-1",
  "findings": [
    {
      "clause_type": "Unlimited Liability",
      "severity": "critical",
      "description": "Contract contains unlimited liability clause",
      "evidence_spans": [
        {
          "document_id": "uuid-1",
          "page": 3,
          "start_char": 100,
          "end_char": 150,
          "text": "..."
        }
      ],
      "recommendation": "Negotiate a cap on liability exposure"
    }
  ],
  "summary": "Found 3 risk findings: 1 critical, 2 high, 0 medium"
}
```

---

#### GET /audit/findings/{document_id}
Get audit findings for a document.

**Parameters:**
- `severity` (optional): Filter by severity (critical, high, medium, low)

**Response:**
```json
[
  {
    "id": "finding-1",
    "clause_type": "Unlimited Liability",
    "severity": "critical",
    "description": "...",
    "evidence": {},
    "recommendation": "...",
    "audit_date": "2025-01-15T10:35:00Z"
  }
]
```

---

#### GET /audit/summary/{document_id}
Get audit summary for a document.

**Response:**
```json
{
  "document_id": "uuid-1",
  "total_findings": 3,
  "by_severity": {
    "critical": 1,
    "high": 2,
    "medium": 0,
    "low": 0
  },
  "risk_level": "HIGH"
}
```

---

### 5. Admin API

#### GET /admin/healthz
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-15T10:00:00Z",
  "version": "1.0.0"
}
```

**Status Codes:**
- 200: Healthy
- 503: Unhealthy

---

#### GET /admin/metrics
Get system metrics.

**Response:**
```json
{
  "documents_ingested": 15,
  "total_queries": 42,
  "total_audit_runs": 8,
  "uptime_seconds": 3600,
  "average_extraction_time_ms": 245,
  "average_qa_time_ms": 450
}
```

---

#### GET /admin/status
Get detailed system status.

**Response:**
```json
{
  "timestamp": "2025-01-15T10:00:00Z",
  "uptime_seconds": 3600,
  "system": {
    "memory_percent": 45.2,
    "cpu_percent": 12.5,
    "num_threads": 8
  },
  "database": {
    "documents": 15,
    "queries": 42,
    "audit_findings": 24
  }
}
```

---

#### POST /admin/reset
Reset system (development only).

**Response:**
```json
{
  "message": "System reset successfully"
}
```

---

### 6. Webhooks API

#### POST /webhooks/register
Register a webhook for events.

**Request:**
```json
{
  "url": "https://your-webhook-url.com/events",
  "events": ["extraction_complete", "audit_complete"]
}
```

**Response:**
```json
{
  "webhook_id": "webhook-uuid",
  "url": "https://your-webhook-url.com/events",
  "events": ["extraction_complete", "audit_complete"],
  "status": "active"
}
```

---

#### GET /webhooks/list
List registered webhooks.

**Response:**
```json
[
  {
    "id": "webhook-uuid",
    "url": "https://...",
    "events": ["extraction_complete"],
    "active": true,
    "created_at": "2025-01-15T09:00:00Z"
  }
]
```

---

#### DELETE /webhooks/{webhook_id}
Unregister a webhook.

**Response:**
```json
{
  "message": "Webhook unregistered"
}
```

---

## Data Types

### Document
```json
{
  "document_id": "string (UUID)",
  "filename": "string",
  "pages": "integer",
  "size": "integer (bytes)",
  "upload_date": "string (ISO 8601)",
  "processing_time_ms": "float"
}
```

### ContractFields
```json
{
  "document_id": "string",
  "parties": ["string"],
  "effective_date": "string (optional)",
  "term": "string (optional)",
  "governing_law": "string (optional)",
  "payment_terms": "string (optional)",
  "termination": "string (optional)",
  "auto_renewal": "string (optional)",
  "confidentiality": "string (optional)",
  "indemnity": "string (optional)",
  "liability_cap": {
    "amount": "string",
    "currency": "string"
  },
  "signatories": [
    {
      "name": "string",
      "title": "string (optional)"
    }
  ]
}
```

### RiskFinding
```json
{
  "clause_type": "string",
  "severity": "critical | high | medium | low | info",
  "description": "string",
  "evidence_spans": [
    {
      "document_id": "string",
      "page": "integer",
      "start_char": "integer",
      "end_char": "integer",
      "text": "string"
    }
  ],
  "recommendation": "string (optional)"
}
```

### WebhookEvent
```json
{
  "event_type": "string (extraction_complete | audit_complete)",
  "task_id": "string (document_id)",
  "timestamp": "string (ISO 8601)",
  "data": {
    "fields_id or findings_count": "string or integer",
    "extraction_time_ms or audit_time_ms": "float"
  },
  "error": "string (optional)"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 404 Not Found
```json
{
  "detail": "Document not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently unlimited. In production, implement:
- 100 requests per minute per client IP
- 10 concurrent connections per API key

---

## Pagination

Supported on list endpoints:
- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum items to return (default: 10, max: 100)

---

## Sorting

Supported sort orders:
- `upload_date` (descending by default)
- `filename`
- `pages`
- `size`

---

## Filtering

Supported filters:
- By document filename
- By audit severity
- By date range

---

## Versioning

Current version: `1.0.0`

API versioning via URL path:
```
/v1/ingest
/v2/ingest
```

---

## Changelog

### 1.0.0 (2025-01-15)
- Initial release
- Basic ingestion, extraction, Q&A, and audit
- Webhook support
- Local and OpenAI LLM providers
