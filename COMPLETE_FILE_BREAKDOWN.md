# 📋 Complete File Breakdown & Working Explanation

## 🎯 Project Overview in One Page

**What:** Smart Contract Analysis System
**Built With:** FastAPI + Python + AI (ChatGPT)
**Purpose:** Upload contracts → Extract info → Detect risks → Ask questions
**Status:** ✅ Running on http://127.0.0.1:8888

---

## 📂 All Files Explained

### **ROOT LEVEL FILES**

```
contract-intelligence-api/
├── main.py                          ← Can also run from here (alternative entry)
├── requirements.txt                 ← All dependencies (full)
├── requirements_minimal.txt         ← Core dependencies only
├── .env.example                     ← Configuration template
├── .gitignore                       ← Git ignore rules
│
├── client.py                        ← Python SDK (makes API easy to use)
├── examples.py                      ← Code examples & workflows
├── utils.py                         ← Development utilities
├── test_api.sh                      ← Bash tests (curl commands)
│
├── Dockerfile                       ← Docker image definition
├── docker-compose.yml               ← Docker setup file
│
└── Documentation (README, guides, etc.)
```

---

## 🏗️ APPLICATION LAYER (`app/`)

### **1. Entry Point**

**File:** `app/main.py`
```python
Purpose: Start the application
When run: Initializes FastAPI server
Does:
  - Import all API routes (ingest, extract, ask, audit, admin, webhooks)
  - Create database tables
  - Add CORS middleware (allow cross-origin requests)
  - Set up logging
  - Define root endpoint "/"
  
Result: Web server running at http://127.0.0.1:8888
```

---

### **2. Configuration**

**File:** `app/core/config.py`
```python
Purpose: Centralized settings
What it stores:
  - API title, version, description
  - Database URL (SQLite path)
  - LLM provider (openai, anthropic, local)
  - API keys (OpenAI, Anthropic)
  - File upload limits
  - Vector store settings
  
How used: Imported everywhere as:
  settings = get_settings()
  settings.database_url
  settings.llm_provider
```

**File:** `app/core/logger.py`
```python
Purpose: Logging setup
Logs: All important events with timestamps
Example: "2025-12-04 17:04:18 - INFO - Starting API v1.0.0"
```

---

### **3. Data Models**

**File:** `app/models/database.py`
```python
Purpose: Define database structure (what data is stored where)

Tables created:
┌─ contracts
│  ├─ id (unique ID)
│  ├─ filename (e.g., "agreement.pdf")
│  ├─ raw_text (full text extracted)
│  ├─ pages (number of pages)
│  ├─ upload_date (when uploaded)
│  └─ processed (status flag)
│
├─ extracted_fields
│  ├─ id
│  ├─ contract_id (which contract)
│  ├─ parties (company names)
│  ├─ effective_date, term, governing_law, etc.
│  └─ extraction_time_ms (performance metric)
│
├─ audit_findings
│  ├─ id
│  ├─ contract_id
│  ├─ finding_type (e.g., "Auto-renewal")
│  ├─ severity (CRITICAL, HIGH, MEDIUM, LOW)
│  ├─ description
│  └─ recommendation
│
├─ query_logs
│  ├─ id
│  ├─ question (what user asked)
│  ├─ answer (what system returned)
│  └─ created_date
│
└─ webhook_events
   ├─ id
   ├─ webhook_url
   ├─ event_type (extraction_complete, audit_complete)
   ├─ status (success, failed)
   └─ created_at

Uses: SQLAlchemy ORM (object-relational mapping)
Database: SQLite3 (file-based, no setup needed)
Location: data/db/contracts.db
```

**File:** `app/models/schemas.py`
```python
Purpose: Define request/response formats (what data comes in/out of API)

Key schemas:
├─ IngestRequest
│  └─ files: List of PDF files to upload
│
├─ IngestResponse
│  └─ documents: List of uploaded documents with IDs
│
├─ ContractFields
│  ├─ parties: List[str]
│  ├─ effective_date: str
│  ├─ term: str
│  ├─ payment_terms: str
│  ├─ liability_cap: dict
│  └─ ... (11 more fields)
│
├─ AskRequest
│  ├─ question: str (what to ask)
│  ├─ document_ids: List[str] (which contracts)
│  └─ top_k: int (how many results)
│
├─ AskResponse
│  ├─ answer: str
│  ├─ source: str (where in document)
│  └─ confidence: float (0-1 score)
│
├─ AuditResponse
│  ├─ findings: List[RiskFinding]
│  └─ severity_summary: dict
│
└─ ... (10+ more schemas)

Uses: Pydantic (data validation library)
```

---

### **4. Services (Business Logic)**

**File:** `app/services/pdf_service.py`
```python
Purpose: Extract text from PDF files

Classes:
├─ PDFExtractor
│  └─ extract_text(file_path)
│     ├─ Uses: pdfplumber library
│     ├─ Reads: Each page of PDF
│     ├─ Returns: (full_text, page_count)
│     └─ Used by: ingest.py when file uploaded
│
└─ PDFMetadata
   └─ get_metadata(file_path)
      ├─ Extracts: Title, Author, Subject, Creator, Producer
      ├─ Uses: PyPDF library
      └─ Returns: dict with metadata

Example:
  pdf = PDFExtractor()
  text, pages = pdf.extract_text("contract.pdf")
  # Returns: ("Company A agrees to...", 10)
```

**File:** `app/services/llm_service.py`
```python
Purpose: AI/ChatGPT integration

Classes:
├─ LLMProvider (Abstract base)
│  └─ Interface for all providers
│
├─ OpenAIProvider (ChatGPT)
│  ├─ Uses: OpenAI API
│  ├─ Model: gpt-4-turbo-preview
│  ├─ async extract_fields(text)
│  │  └─ Asks ChatGPT: "Extract parties, dates, terms from this contract"
│  ├─ async answer_question(question, context)
│  │  └─ Asks ChatGPT: "Answer this based on this contract section"
│  └─ async detect_risks(text)
│     └─ Asks ChatGPT: "What are the risky clauses?"
│
├─ AnthropicProvider (Claude)
│  └─ Same interface but uses Anthropic API instead
│
└─ LocalLLMProvider (Fallback)
   ├─ No API needed (works offline)
   ├─ Uses: Regex patterns and rules
   ├─ Extracts: Basic fields using string matching
   └─ Used: When OpenAI API unavailable

Example:
  llm = OpenAIProvider(api_key="sk-...")
  fields = await llm.extract_fields("Company A and Company B agree...")
  # Returns: {parties: ["Company A", "Company B"], ...}
```

**File:** `app/services/embedding_service.py`
```python
Purpose: Vector search (semantic search for Q&A)

Classes:
├─ EmbeddingService
│  ├─ Uses: Sentence-Transformers (all-MiniLM-L6-v2 model)
│  ├─ embed_text(text)
│  │  └─ Converts: "The payment term is Net 30" → [0.12, -0.45, 0.89, ...]
│  └─ embed_query(query)
│     └─ Converts: "payment?" → [0.10, -0.43, 0.91, ...]
│
└─ VectorStore
   ├─ Uses: ChromaDB (vector database)
   ├─ add_text(text, document_id)
   │  └─ Stores: Text embeddings in vector database
   └─ search(query, top_k=5)
      └─ Finds: Most similar paragraphs using cosine similarity

How it works:
  1. User asks: "What is payment term?"
  2. embedding_service converts to vector
  3. VectorStore searches ChromaDB
  4. Returns top 5 most similar paragraphs
  5. llm_service extracts answer from those paragraphs

Example:
  embeddings = EmbeddingService()
  vector_store = VectorStore()
  vector_store.add_text("Net 30 payment terms", doc_id="doc-123")
  results = vector_store.search("payment?")
  # Returns: ["Net 30 payment terms", ...]
```

**File:** `app/services/webhook_service.py`
```python
Purpose: Send event notifications to external systems

Class:
└─ WebhookManager
   ├─ register_webhook(url, events)
   │  └─ Saves webhook URL to database
   │     Events can be: ["extraction_complete", "audit_complete"]
   │
   ├─ emit_event(event_type, document_id, payload)
   │  └─ When event happens:
   │     ├─ Find all webhooks for this event
   │     ├─ POST data to webhook URL
   │     ├─ Retry if delivery fails (up to 3 times)
   │     └─ Log result in webhook_events table
   │
   └─ get_retry_delay(attempt)
      └─ Backoff: 1s, 2s, 4s

Example:
  manager = WebhookManager(db)
  
  # User registers webhook
  await manager.register_webhook(
    url="https://your-system.com/notify",
    events=["extraction_complete"]
  )
  
  # When extraction finishes
  await manager.emit_event(
    "extraction_complete",
    "doc-123",
    {fields: {...}}
  )
  # Sends: POST https://your-system.com/notify
  #        {event: "extraction_complete", document_id: "doc-123", fields: {...}}
```

---

### **5. API Endpoints**

**File:** `app/api/ingest.py` 📤
```python
Purpose: Handle PDF uploads and document management

Endpoints:
├─ POST /ingest
│  ├─ Input: Files (form-data)
│  ├─ Does:
│  │  ├─ Validate files (PDF? <50MB?)
│  │  ├─ Save to data/uploads/
│  │  ├─ Extract text with pdf_service
│  │  ├─ Store in contracts table
│  │  └─ Return document IDs
│  └─ Example:
│     curl -X POST http://localhost:8888/ingest -F "files=@contract.pdf"
│     Returns: {documents: [{id: "doc-123", filename: "contract.pdf", pages: 10}]}
│
├─ GET /ingest/documents
│  ├─ Does: List all uploaded documents (paginated)
│  └─ Example: curl http://localhost:8888/ingest/documents?skip=0&limit=10
│
├─ GET /ingest/documents/{document_id}
│  ├─ Does: Get details of one document
│  └─ Example: curl http://localhost:8888/ingest/documents/doc-123
│
└─ DELETE /ingest/documents/{document_id}
   ├─ Does: Delete document and all related data
   └─ Example: curl -X DELETE http://localhost:8888/ingest/documents/doc-123
```

**File:** `app/api/extract.py` 🔍
```python
Purpose: Extract structured information from contracts

Endpoints:
├─ POST /extract
│  ├─ Input: document_id (query param)
│  ├─ Does:
│  │  ├─ Get contract text from database
│  │  ├─ Call llm_service.extract_fields()
│  │  ├─ Uses ChatGPT to analyze and extract
│  │  ├─ Save to extracted_fields table
│  │  ├─ Emit webhook: "extraction_complete"
│  │  └─ Return extracted fields
│  └─ Example:
│     curl -X POST http://localhost:8888/extract?document_id=doc-123
│     Returns: {
│       parties: ["Company A", "Company B"],
│       effective_date: "2025-01-01",
│       term: "3 years",
│       payment_terms: "Net 30",
│       ...
│     }
│
└─ GET /extract/fields/{document_id}
   ├─ Does: Get previously extracted fields from database
   └─ Example: curl http://localhost:8888/extract/fields/doc-123
```

**File:** `app/api/ask.py` ❓
```python
Purpose: Question & Answer system using RAG (Retrieval-Augmented Generation)

Endpoints:
├─ POST /ask
│  ├─ Input: {question: "...", document_ids: [...], top_k: 5}
│  ├─ Does:
│  │  ├─ Convert question to embedding (embedding_service)
│  │  ├─ Search vector database for similar text (top_k results)
│  │  ├─ Get context from those paragraphs
│  │  ├─ Ask ChatGPT to answer based on context
│  │  ├─ Record in query_logs table
│  │  └─ Return answer with source
│  └─ Example:
│     curl -X POST http://localhost:8888/ask \
│       -H "Content-Type: application/json" \
│       -d '{
│         "question": "What is the payment term?",
│         "document_ids": ["doc-123"],
│         "top_k": 5
│       }'
│     Returns: {
│       answer: "The payment term is Net 30.",
│       source: "Page 3, Section 4.1",
│       confidence: 0.92
│     }
│
├─ GET /ask/stream
│  ├─ Returns: Server-Sent Events (streaming tokens as they arrive)
│  ├─ Used for: Real-time UI updates
│  └─ Example: curl http://localhost:8888/ask/stream?question=payment?&document_ids=doc-123
│
└─ GET /ask/queries
   ├─ Does: Return query history
   └─ Example: curl http://localhost:8888/ask/queries?skip=0&limit=10
```

**File:** `app/api/audit.py` ⚠️
```python
Purpose: Risk detection and contract auditing

Endpoints:
├─ POST /audit
│  ├─ Input: document_id (query param)
│  ├─ Does:
│  │  ├─ Get contract text
│  │  ├─ Call llm_service.detect_risks()
│  │  ├─ Looks for:
│  │  │  ├─ Auto-renewal <30 days notice
│  │  │  ├─ Unlimited liability
│  │  │  ├─ Broad indemnification
│  │  │  ├─ Unfavorable payment terms
│  │  │  ├─ Restricted termination
│  │  │  └─ Confidentiality issues
│  │  ├─ Save to audit_findings table
│  │  ├─ Emit webhook: "audit_complete"
│  │  └─ Return findings with recommendations
│  └─ Example:
│     curl -X POST http://localhost:8888/audit?document_id=doc-123
│     Returns: {
│       findings: [
│         {
│           type: "Auto-renewal",
│           severity: "HIGH",
│           description: "Only 10 days notice required",
│           recommendation: "Negotiate for 90 days notice"
│         },
│         {
│           type: "Liability",
│           severity: "CRITICAL",
│           description: "No liability cap specified",
│           recommendation: "Add liability limit clause"
│         }
│       ]
│     }
│
├─ GET /audit/findings/{document_id}
│  ├─ Does: Get audit findings from database
│  └─ Example: curl http://localhost:8888/audit/findings/doc-123
│
└─ GET /audit/summary/{document_id}
   ├─ Does: Get risk summary (severity counts)
   └─ Example: curl http://localhost:8888/audit/summary/doc-123
```

**File:** `app/api/admin.py` 📊
```python
Purpose: System monitoring and health

Endpoints:
├─ GET /admin/healthz
│  ├─ Does: Check if system is healthy
│  └─ Returns: {status: "healthy", timestamp: "...", uptime_seconds: 120}
│
├─ GET /admin/metrics
│  ├─ Does: Get performance metrics
│  └─ Returns: {
│       documents_ingested: 5,
│       total_queries: 42,
│       total_audit_runs: 3,
│       average_extraction_time_ms: 2340,
│       average_qa_time_ms: 1250,
│       memory_mb: 256,
│       cpu_percent: 15
│     }
│
├─ GET /admin/status
│  ├─ Does: Get detailed system status
│  └─ Returns: LLM provider, vector store, database info
│
└─ POST /admin/reset
   ├─ Does: Clear all data (testing only)
   └─ Removes: All documents, findings, query logs, webhooks
```

**File:** `app/api/webhooks.py` 🔔
```python
Purpose: Manage event webhooks

Endpoints:
├─ POST /webhooks/register
│  ├─ Input: {url: "...", events: ["extraction_complete"]}
│  ├─ Does:
│  │  ├─ Validate webhook URL
│  │  ├─ Save to database
│  │  └─ Test delivery (optional)
│  └─ Example:
│     curl -X POST http://localhost:8888/webhooks/register \
│       -H "Content-Type: application/json" \
│       -d '{
│         "url": "https://your-system.com/notify",
│         "events": ["extraction_complete", "audit_complete"]
│       }'
│
├─ GET /webhooks/list
│  ├─ Does: List all registered webhooks
│  └─ Returns: List of webhook URLs and their events
│
└─ DELETE /webhooks/{webhook_id}
   ├─ Does: Unregister a webhook
   └─ Example: curl -X DELETE http://localhost:8888/webhooks/webhook-123
```

---

## 🛠️ Helper Files

**`client.py` - Python SDK**
```python
Purpose: Python wrapper for the API (easier than HTTP calls)

Usage:
  from client import ContractIntelligenceClient
  
  client = ContractIntelligenceClient("http://localhost:8888")
  
  # Upload
  docs = await client.ingest(["contract.pdf"])
  
  # Extract
  fields = await client.extract(docs[0])
  
  # Ask
  answer = await client.ask(
    question="Payment terms?",
    document_ids=[docs[0]]
  )
  
  # Audit
  risks = await client.audit(docs[0])
```

**`examples.py` - Code Examples**
```python
Shows:
  - How to upload contracts
  - How to extract fields
  - How to ask questions
  - How to detect risks
  - How to register webhooks
  - How to handle responses
```

**`utils.py` - Dev Utilities**
```python
Commands:
  python utils.py install      ← Install dependencies
  python utils.py setup-db     ← Setup database
  python utils.py run          ← Start server
  python utils.py build        ← Build Docker image
  python utils.py docker       ← Run Docker container
```

---

## 📊 Complete File Inventory

| Layer | File | Type | Lines | Purpose |
|-------|------|------|-------|---------|
| **Entry** | app/main.py | Python | 91 | Start app |
| **Config** | app/core/config.py | Python | 58 | Settings |
| **Config** | app/core/logger.py | Python | 20 | Logging |
| **Models** | app/models/database.py | Python | 106 | ORM tables |
| **Models** | app/models/schemas.py | Python | 150 | Data validation |
| **Services** | app/services/pdf_service.py | Python | 55 | PDF extraction |
| **Services** | app/services/llm_service.py | Python | 292 | AI integration |
| **Services** | app/services/embedding_service.py | Python | 130 | Vector search |
| **Services** | app/services/webhook_service.py | Python | 85 | Webhooks |
| **API** | app/api/ingest.py | Python | 190 | Upload endpoints |
| **API** | app/api/extract.py | Python | 156 | Extraction endpoints |
| **API** | app/api/ask.py | Python | 200 | Q&A endpoints |
| **API** | app/api/audit.py | Python | 180 | Audit endpoints |
| **API** | app/api/admin.py | Python | 120 | Admin endpoints |
| **API** | app/api/webhooks.py | Python | 110 | Webhook endpoints |
| **Tests** | tests/test_api.py | Python | 200 | Pytest tests |
| **Docs** | README.md | Markdown | 400 | Quick start |
| **Docs** | API_SPEC.md | Markdown | 300 | API docs |
| **Docs** | DEPLOYMENT.md | Markdown | 400 | Deployment |
| **Docs** | PROJECT_EXPLANATION.md | Markdown | 800 | Detailed guide |
| **Docs** | ARCHITECTURE_GUIDE.md | Markdown | 600 | Diagrams |
| **Docker** | docker-compose.yml | YAML | 30 | Docker setup |
| **Docker** | Dockerfile | Docker | 25 | Image def |
| **Config** | requirements.txt | Text | 25 | Dependencies |
| **Config** | .env.example | Env | 15 | Config template |
| **Utils** | client.py | Python | 300 | Python SDK |
| **Utils** | examples.py | Python | 250 | Examples |
| **Utils** | utils.py | Python | 150 | Dev tools |

**TOTAL: 42 files, 6000+ lines of code and documentation**

---

## 🎯 Quick Navigation

**Want to understand:**
- PDF upload? → `ingest.py`
- Field extraction? → `extract.py` + `llm_service.py`
- Risk detection? → `audit.py` + `llm_service.py`
- Q&A system? → `ask.py` + `embedding_service.py`
- Database? → `database.py`
- API calls? → `client.py` or `examples.py`
- Configuration? → `config.py` + `.env.example`
- How it starts? → `main.py`

---

## ✅ Everything Is Ready!

The system has:
- ✅ 21 API endpoints
- ✅ Full database (SQLite)
- ✅ AI integration (ChatGPT)
- ✅ Vector search (semantic)
- ✅ Webhook support
- ✅ Risk detection
- ✅ Complete documentation
- ✅ Python SDK
- ✅ Docker support

**Status: RUNNING on http://127.0.0.1:8888** 🎉
