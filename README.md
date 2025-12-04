# Contract Intelligence API

A production-ready Contract Intelligence and Risk Audit System built with FastAPI. The system ingests PDFs, extracts structured fields, answers questions over contracts using RAG, and identifies risky clauses.

## Features

- **PDF Ingestion**: Upload and process multiple PDFs with automatic text extraction
- **Structured Extraction**: Extract key contract fields (parties, dates, terms, liability caps, etc.)
- **Question Answering**: RAG-based Q&A grounded in uploaded documents with citations
- **Risk Audit**: Automatic detection of risky clauses with severity levels and recommendations
- **Streaming**: SSE/WebSocket streaming for real-time token streaming
- **Webhooks**: Event-driven architecture with configurable webhooks
- **Vector Search**: Semantic search using embeddings (ChromaDB/local fallback)
- **Admin Dashboard**: Health checks, metrics, and system monitoring
- **Local LLM Support**: Works with local LLM providers or OpenAI/Anthropic APIs

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (if running locally)
- OpenAI API key (optional, uses local LLM by default)

### Docker (Recommended)

```bash
cd contract-intelligence-api

# Create .env file
cp .env.example .env

# Start the service
docker-compose up -d

# API will be available at http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Create database
python -c "from app.models.database import create_tables; from app.core.config import get_settings; create_tables(get_settings().database_url)"

# Run server
python main.py

# Access at http://localhost:8000
```

## API Endpoints

### Ingestion

```bash
# Upload PDFs
curl -X POST "http://localhost:8000/ingest" \
  -F "files=@contract1.pdf" \
  -F "files=@contract2.pdf"

# List documents
curl "http://localhost:8000/ingest/documents"

# Get document details
curl "http://localhost:8000/ingest/documents/{document_id}"

# Delete document
curl -X DELETE "http://localhost:8000/ingest/documents/{document_id}"
```

### Field Extraction

```bash
# Extract structured fields
curl -X POST "http://localhost:8000/extract?document_id={document_id}"

# Get previously extracted fields
curl "http://localhost:8000/extract/fields/{document_id}"
```

### Question Answering

```bash
# Ask a question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the payment term?",
    "document_ids": ["{document_id}"],
    "top_k": 5
  }'

# Stream answer tokens
curl "http://localhost:8000/ask/stream?question=What%20is%20the%20termination%20clause%3F"

# Get query history
curl "http://localhost:8000/ask/queries"
```

### Risk Audit

```bash
# Run audit on contract
curl -X POST "http://localhost:8000/audit?document_id={document_id}"

# Get audit findings
curl "http://localhost:8000/audit/findings/{document_id}"

# Get audit summary
curl "http://localhost:8000/audit/summary/{document_id}"
```

### Admin & Monitoring

```bash
# Health check
curl "http://localhost:8000/admin/healthz"

# Get metrics
curl "http://localhost:8000/admin/metrics"

# Get detailed status
curl "http://localhost:8000/admin/status"
```

### Webhooks

```bash
# Register webhook
curl -X POST "http://localhost:8000/webhooks/register" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-webhook-url.com/events",
    "events": ["extraction_complete", "audit_complete"]
  }'

# List webhooks
curl "http://localhost:8000/webhooks/list"

# Unregister webhook
curl -X DELETE "http://localhost:8000/webhooks/{webhook_id}"
```

## Configuration

Edit `.env` to customize:

```env
# LLM Provider (local, openai, anthropic)
LLM_PROVIDER=local
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4-turbo-preview

# Database
DATABASE_URL=sqlite:///./data/db/contracts.db

# Vector Store
VECTOR_STORE_TYPE=chromadb
CHROMADB_DIR=./data/chroma

# File Upload
MAX_FILE_SIZE=50  # MB
```

## Sample Contracts

The system works with any contract PDFs. Here are recommended open-source contracts for testing:

1. **NDA Template**: https://www.contractstandards.com/nda
2. **MSA Template**: https://www.contractstandards.com/msa
3. **Service Agreement**: https://www.worldwildlife.org/tos
4. **Terms of Service**: https://github.com/github/site-policy
5. **Open Source License**: https://opensource.org/licenses/MIT

For local testing, you can use any PDF contracts. The API will automatically extract text and make it searchable.

## Data Models

### Contract Fields

Automatically extracted fields include:
- `parties`: List of contracting parties
- `effective_date`: Contract start date
- `term`: Contract duration
- `governing_law`: Jurisdiction
- `payment_terms`: Payment conditions
- `termination`: Termination clauses
- `auto_renewal`: Auto-renewal terms
- `confidentiality`: NDA/confidentiality clauses
- `indemnity`: Indemnification terms
- `liability_cap`: Liability limits (amount + currency)
- `signatories`: Signing parties with titles

### Risk Findings

Detected risks include:
- **Clause Type**: Type of risky clause
- **Severity**: CRITICAL, HIGH, MEDIUM, LOW
- **Description**: What makes it risky
- **Evidence**: Text span from contract
- **Recommendation**: How to mitigate

Common risks detected:
- Auto-renewal with <30 days notice
- Unlimited liability clauses
- Broad indemnification
- Unfavorable payment terms
- Restrictive termination
- Excessive confidentiality restrictions

## Architecture

```
contract-intelligence-api/
├── app/
│   ├── api/
│   │   ├── ingest.py      # PDF upload & storage
│   │   ├── extract.py     # Field extraction
│   │   ├── ask.py         # RAG Q&A
│   │   ├── audit.py       # Risk detection
│   │   ├── admin.py       # Health/metrics
│   │   └── webhooks.py    # Event dispatch
│   ├── services/
│   │   ├── pdf_service.py        # PDF extraction
│   │   ├── llm_service.py        # LLM providers
│   │   ├── embedding_service.py  # Vector embeddings
│   │   └── webhook_service.py    # Webhook management
│   ├── models/
│   │   ├── schemas.py    # Pydantic models
│   │   └── database.py   # SQLAlchemy models
│   ├── core/
│   │   ├── config.py     # Settings
│   │   └── logger.py     # Logging
│   └── main.py          # FastAPI app
├── data/
│   ├── uploads/         # PDF files
│   ├── db/              # SQLite database
│   └── chroma/          # Vector embeddings
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── main.py              # Entry point
└── README.md
```

## LLM Integration

### Local Mode (Default)

Uses regex patterns and keyword matching. Limited but works offline:

```bash
LLM_PROVIDER=local
```

### OpenAI

Requires API key:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4-turbo-preview
```

### Anthropic

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
```

## Database

The system uses SQLite by default (no extra setup needed). For production, you can use:

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/contracts

# MySQL
DATABASE_URL=mysql://user:password@localhost:3306/contracts
```

## Performance Metrics

Track performance via `/admin/metrics`:

- `documents_ingested`: Total PDFs processed
- `total_queries`: Q&A queries executed
- `total_audit_runs`: Risk audits performed
- `uptime_seconds`: System uptime
- `average_extraction_time_ms`: Avg field extraction time
- `average_qa_time_ms`: Avg Q&A response time

## Webhook Events

The system emits two event types:

```json
{
  "event_type": "extraction_complete",
  "task_id": "document_id",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "fields_id": "...",
    "extraction_time_ms": 245
  }
}
```

```json
{
  "event_type": "audit_complete",
  "task_id": "document_id",
  "timestamp": "2025-01-15T10:31:00Z",
  "data": {
    "findings_count": 3,
    "critical_count": 1,
    "high_count": 2,
    "audit_time_ms": 512
  }
}
```

## Error Handling

All endpoints return structured error responses:

```json
{
  "detail": "Document not found"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Bad request
- `404`: Not found
- `500`: Server error

## Security Considerations

- API should be behind authentication in production
- Implement rate limiting per client
- Use HTTPS only in production
- Validate file uploads
- Sanitize user inputs
- Encrypt sensitive data at rest

## Testing

```bash
# Using curl
./test_api.sh

# Using pytest
pytest tests/

# Using Python requests
python -m pytest -v
```

## Troubleshooting

### PDF Extraction Issues

If PDFs aren't extracting properly, check:
- File is valid PDF format
- PDF isn't password-protected
- File isn't corrupted

### LLM Timeout

If extraction/audit is slow:
- Switch to local LLM provider
- Reduce document size
- Check API rate limits

### Database Lock

If getting database lock errors:
- Ensure write permissions to `data/` directory
- Stop all running instances
- Delete `.db-wal` and `.db-shm` files if present

## Production Deployment

For production:

1. Use PostgreSQL/MySQL instead of SQLite
2. Enable HTTPS
3. Add authentication/authorization
4. Configure API rate limiting
5. Use Kubernetes for orchestration
6. Add monitoring (Prometheus, Datadog)
7. Enable request logging
8. Set up backups
9. Use managed LLM APIs (OpenAI, Anthropic)

## API Documentation

Full interactive documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Contributing

Issues, feature requests, and PRs welcome!

## License

MIT License - See LICENSE file

## Support

For issues or questions:
1. Check the docs at `/docs`
2. Review logs in `logs/` directory
3. Check system status at `/admin/status`
