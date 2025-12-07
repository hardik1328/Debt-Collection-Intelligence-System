# 🎨 Contract Intelligence API - Visual Architecture Guide

## 📐 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER/CLIENT                                   │
│          (Browser, API Client, Mobile App)                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
        ┌────────────────────────────────────┐
        │      FASTAPI WEB SERVER             │
        │   (app/main.py)                     │
        │                                     │
        │  • CORS Middleware                  │
        │  • Request Routing                  │
        │  • Error Handling                   │
        └──────────────┬──────────────────────┘
                       │
        ┌──────────────┼──────────────────────┐
        │              │                      │
        ↓              ↓                      ↓
    ┌─────────┐  ┌──────────┐          ┌──────────┐
    │ INGEST  │  │ EXTRACT  │   ...    │ WEBHOOKS │
    │ ROUTER  │  │ ROUTER   │          │ ROUTER   │
    │(Upload) │  │(Analyze) │          │(Notify)  │
    └────┬────┘  └────┬─────┘          └────┬─────┘
         │            │                      │
         └────────────┼──────────────────────┘
                      ↓
        ┌─────────────────────────────────────┐
        │      SERVICES LAYER                 │
        │  (Business Logic)                   │
        │                                     │
        │  ┌──────────────────────────────┐  │
        │  │ PDF Service                  │  │
        │  │ • Extract text from PDFs     │  │
        │  │ • Get metadata               │  │
        │  └──────────────────────────────┘  │
        │                                     │
        │  ┌──────────────────────────────┐  │
        │  │ LLM Service                  │  │
        │  │ • OpenAI (ChatGPT)           │  │
        │  │ • Anthropic (Claude)         │  │
        │  │ • Local AI (fallback)        │  │
        │  │ • Extract fields             │  │
        │  │ • Detect risks               │  │
        │  │ • Answer questions           │  │
        │  └──────────────────────────────┘  │
        │                                     │
        │  ┌──────────────────────────────┐  │
        │  │ Embedding Service            │  │
        │  │ • Convert text to vectors    │  │
        │  │ • Semantic search            │  │
        │  └──────────────────────────────┘  │
        │                                     │
        │  ┌──────────────────────────────┐  │
        │  │ Webhook Service              │  │
        │  │ • Register hooks             │  │
        │  │ • Send notifications         │  │
        │  │ • Retry logic                │  │
        │  └──────────────────────────────┘  │
        └─────────┬──────────────────────────┘
                  │
        ┌─────────┼──────────────────────┐
        │         │                      │
        ↓         ↓                      ↓
    ┌────────┐ ┌────────────┐      ┌────────────┐
    │DATABASE│ │VECTOR DB   │      │EXTERNAL    │
    │(SQLite)│ │(ChromaDB)  │      │WEBHOOKS    │
    │        │ │            │      │            │
    │Tables: │ │ • Stores   │      │Receives:   │
    │• Contract
    │• Extract
    │• Audit │ │   embeddings
    │• Queries│ │ • Fast     │      │• Events    │
    │• Webhooks
    │        │ │   search   │      │• Results   │
    └────────┘ └────────────┘      └────────────┘
```

---

## 📊 Data Flow Diagrams

### **1. PDF Upload & Storage**

```
User uploads contract.pdf
         ↓
    ingest.py
         ↓
    Validate file (PDF? <50MB?)
         ↓
    Save to data/uploads/
         ↓
    pdf_service.py extracts text
         ↓
    Store in SQLite:
    ├─ contracts table
    │  ├─ id: doc-123
    │  ├─ filename: contract.pdf
    │  ├─ raw_text: "Company A Inc..."
    │  ├─ pages: 10
    │  └─ upload_date: 2025-12-04
    │
    └─ Return to user: {document_id: "doc-123"}
```

---

### **2. Field Extraction**

```
User requests: POST /extract?document_id=doc-123
         ↓
    extract.py
         ↓
    Retrieve document from database
         ↓
    llm_service.py (LLMProvider)
         ↓
    Send to OpenAI/Local AI
    "Extract: parties, dates, terms, etc."
         ↓
    AI analyzes and returns JSON
    {
      "parties": ["Company A", "Company B"],
      "effective_date": "2025-01-01",
      "term": "3 years",
      "payment_terms": "Net 30"
    }
         ↓
    Save to extracted_fields table
         ↓
    Emit webhook: "extraction_complete"
         ↓
    Return to user
```

---

### **3. Risk Audit**

```
User requests: POST /audit?document_id=doc-123
         ↓
    audit.py
         ↓
    Retrieve document from database
         ↓
    llm_service.py analyzes for risks
    Checks for:
    - Auto-renewal <30 days notice?
    - Unlimited liability?
    - Unfair payment terms?
    - Restricted termination?
         ↓
    AI detects risks
         ↓
    Save findings to audit_findings table:
    {
      "type": "Auto-renewal",
      "severity": "HIGH",
      "description": "Only 10 days notice",
      "recommendation": "Negotiate 90 days"
    }
         ↓
    Emit webhook: "audit_complete"
         ↓
    Return to user
```

---

### **4. Question & Answer**

```
User asks: "What are payment terms?"
         ↓
    ask.py
         ↓
    embedding_service.py converts:
    "What are payment terms?" → [0.12, -0.45, 0.89, ...]
                                (numeric vector)
         ↓
    Search ChromaDB vector database
    Find paragraphs with similar meaning
    Results: [
      "Payment due Net 30",
      "Invoice terms 2/10 Net 30",
      "Payment within 30 days"
    ]
         ↓
    llm_service.py extracts answer
    Using: question + context
    → "Payment terms are Net 30, due within 30 days"
         ↓
    query_logs table records:
    - Question asked
    - Answer given
    - Timestamp
         ↓
    Return to user with source
```

---

### **5. Webhook Notification**

```
Event triggers: "extraction_complete"
         ↓
    webhook_service.py
         ↓
    Get registered webhooks from DB
    Webhooks table:
    [
      {url: "https://your-system.com/notify", events: ["extraction_complete"]},
      {url: "https://slack.com/hook", events: ["extraction_complete"]}
    ]
         ↓
    For each webhook:
      POST to URL with payload:
      {
        "event": "extraction_complete",
        "document_id": "doc-123",
        "fields": {...}
      }
         ↓
    If delivery fails:
      Retry 1... wait 1s
      Retry 2... wait 2s
      Retry 3... wait 4s
         ↓
    Log result to webhook_events table
```

---

## 🗂️ Directory Structure with Details

```
contract-intelligence-api/
│
├── app/
│   ├── __init__.py                    (Python package marker)
│   ├── main.py                        🚀 Entry point - starts everything
│   │
│   ├── api/                           🔗 API Endpoints
│   │   ├── __init__.py
│   │   ├── ingest.py                  📤 /ingest* routes
│   │   ├── extract.py                 🔍 /extract* routes
│   │   ├── ask.py                     ❓ /ask* routes
│   │   ├── audit.py                   ⚠️  /audit* routes
│   │   ├── admin.py                   📊 /admin* routes
│   │   └── webhooks.py                🔔 /webhooks* routes
│   │
│   ├── services/                      ⚙️  Business Logic
│   │   ├── __init__.py
│   │   ├── pdf_service.py             📄 PDF text extraction
│   │   ├── llm_service.py             🤖 AI/ChatGPT integration
│   │   ├── embedding_service.py       🔤➡️🔢 Vector search
│   │   └── webhook_service.py         🔔 Event notifications
│   │
│   ├── models/                        📋 Data Structures
│   │   ├── __init__.py
│   │   ├── database.py                💾 Database tables & ORM
│   │   └── schemas.py                 📋 Request/response formats
│   │
│   └── core/                          ⚙️  Configuration
│       ├── __init__.py
│       ├── config.py                  🔧 Settings from .env
│       └── logger.py                  📝 Logging setup
│
├── data/                              💾 Persistent Storage
│   ├── uploads/                       📁 Uploaded PDF files
│   ├── db/                            💾 SQLite database
│   │   └── contracts.db               (auto-created)
│   └── chroma/                        🔍 Vector search index
│
├── tests/                             ✅ Test Suite
│   ├── test_api.py                    📝 Pytest tests
│   └── test_api.sh                    📝 Curl tests
│
├── Documentation/                     📖 Project Docs
│   ├── README.md                      Quick start
│   ├── API_SPEC.md                    API reference
│   ├── DEPLOYMENT.md                  How to deploy
│   ├── PROJECT_SUMMARY.md             Technical summary
│   ├── QUICKSTART.md                  30-second setup
│   ├── RESOURCES.md                   External links
│   ├── START_HERE.md                  Getting started
│   ├── INDEX.md                       Project index
│   ├── COMPLETION_REPORT.md           Metrics
│   ├── DELIVERY_SUMMARY.md            What's included
│   └── PROJECT_EXPLANATION.md         📍 This file
│
├── Code Helpers/                      🛠️  Utilities
│   ├── client.py                      🐍 Python SDK
│   ├── examples.py                    💡 Usage examples
│   ├── utils.py                       🔧 Dev utilities
│   └── main.py                        (Root level - entry point option)
│
├── Configuration/                     ⚙️  Setup Files
│   ├── requirements.txt               📚 Dependencies (full)
│   ├── requirements_minimal.txt       📚 Dependencies (core only)
│   ├── .env.example                   🔑 Config template
│   └── .gitignore                     🚫 Git ignore rules
│
├── Docker/                            🐳 Containerization
│   ├── Dockerfile                     Docker image definition
│   └── docker-compose.yml             Multi-container setup
│
└── Git/                               📌 Version Control
    └── .git/                          Git history
```

---

## 🔄 API Endpoint Map

```
┌─────────────────────────────────────────────────────────────────┐
│                    HTTP ENDPOINTS                               │
│                   (21 Total Routes)                              │
└─────────────────────────────────────────────────────────────────┘

INGEST (Upload PDFs)
├─ POST   /ingest                      → Upload files
├─ GET    /ingest/documents            → List documents
├─ GET    /ingest/documents/{id}       → Get document details
└─ DELETE /ingest/documents/{id}       → Delete document

EXTRACT (Extract Fields)
├─ POST   /extract                     → Extract from document
└─ GET    /extract/fields/{id}         → Get extracted fields

ASK (Question & Answer)
├─ POST   /ask                         → Ask question
├─ GET    /ask/stream                  → Stream answer (SSE)
└─ GET    /ask/queries                 → Query history

AUDIT (Risk Detection)
├─ POST   /audit                       → Audit document
├─ GET    /audit/findings/{id}         → Get findings
└─ GET    /audit/summary/{id}          → Get summary

ADMIN (System Monitoring)
├─ GET    /admin/healthz               → Health check
├─ GET    /admin/metrics               → Performance metrics
├─ GET    /admin/status                → System status
└─ POST   /admin/reset                 → Reset data

WEBHOOKS (Event Notifications)
├─ POST   /webhooks/register           → Register webhook
├─ GET    /webhooks/list               → List webhooks
└─ DELETE /webhooks/{id}               → Delete webhook

ROOT
└─ GET    /                            → API info
```

---

## 🛠️ Technology Stack

```
┌────────────────────────────────────────┐
│         TECHNOLOGY STACK               │
├────────────────────────────────────────┤
│                                        │
│  🐍 LANGUAGE: Python 3.13              │
│  📦 RUNTIME: Uvicorn ASGI server       │
│                                        │
├────────────────────────────────────────┤
│         WEB FRAMEWORK                  │
├────────────────────────────────────────┤
│  ⚡ FastAPI 0.123.7                    │
│     • Async/await support              │
│     • Auto-generated docs              │
│     • Built-in validation              │
│                                        │
├────────────────────────────────────────┤
│         DATA VALIDATION                │
├────────────────────────────────────────┤
│  ✓ Pydantic 2.12.5                     │
│     • Schema validation                │
│     • Type checking                    │
│     • JSON serialization               │
│                                        │
├────────────────────────────────────────┤
│         DATABASE                       │
├────────────────────────────────────────┤
│  💾 SQLite (default)                   │
│  🔗 SQLAlchemy 2.0.44 (ORM)            │
│     • Object-Relational Mapping        │
│     • Database abstraction             │
│     • Query builder                    │
│                                        │
├────────────────────────────────────────┤
│         PDF PROCESSING                 │
├────────────────────────────────────────┤
│  📄 PyPDF 6.4.0                        │
│  📄 pdfplumber 0.11.8                  │
│     • Text extraction                  │
│     • Metadata reading                 │
│                                        │
├────────────────────────────────────────┤
│         AI/LANGUAGE MODELS             │
├────────────────────────────────────────┤
│  🤖 OpenAI API (ChatGPT)               │
│  🤖 Anthropic API (Claude)             │
│  🤖 Local LLM (fallback)               │
│     • Field extraction                 │
│     • Risk detection                   │
│     • Question answering               │
│                                        │
├────────────────────────────────────────┤
│         VECTOR SEARCH                  │
├────────────────────────────────────────┤
│  🔤 Sentence-Transformers              │
│     • Text embeddings                  │
│     • Semantic search                  │
│  🔍 ChromaDB                           │
│     • Vector database                  │
│     • Similarity search                │
│                                        │
├────────────────────────────────────────┤
│         HTTP CLIENT                    │
├────────────────────────────────────────┤
│  🌐 aiohttp 3.13.2                     │
│     • Async HTTP requests              │
│     • Webhook delivery                 │
│                                        │
├────────────────────────────────────────┤
│         SYSTEM MONITORING              │
├────────────────────────────────────────┤
│  📊 psutil 7.1.3                       │
│     • CPU/Memory metrics               │
│     • Process monitoring               │
│                                        │
├────────────────────────────────────────┤
│         ASYNC SUPPORT                  │
├────────────────────────────────────────┤
│  ⚡ asyncio (Python std lib)           │
│     • Non-blocking operations          │
│     • Concurrent requests              │
│     • Streaming responses              │
│                                        │
└────────────────────────────────────────┘
```

---

## 📈 Request/Response Flow Example

### **Complete Upload → Extract → Audit → Ask Workflow**

```
CLIENT                          SERVER                          DATABASE
  │                               │                               │
  ├─── 1. POST /ingest ──────────►│                              │
  │       (files: contract.pdf)    │                              │
  │                               ├─ ingest.py                   │
  │                               ├─ Save file                    │
  │                               ├─ pdf_service.py (extract)    │
  │                               ├─ Create DB record ─────────►│
  │                               │  (contracts table)            │
  │                           ◄───┤ 200 OK + doc_id             │
  │◄───────────────────────────────┤ {id: "doc-123"}            │
  │
  ├─── 2. POST /extract ─────────►│                              │
  │   (?document_id=doc-123)       │                              │
  │                               ├─ extract.py                  │
  │                               ├─ llm_service.py (ChatGPT)   │
  │                               ├─ Analysis...                │
  │                               ├─ Save results ──────────────►│
  │                               │  (extracted_fields table)    │
  │                               ├─ webhook_service (notify)   │
  │                           ◄───┤ 200 OK + fields             │
  │◄───────────────────────────────┤ {parties: [...], terms: [...]}
  │
  ├─── 3. POST /audit ───────────►│                              │
  │   (?document_id=doc-123)       │                              │
  │                               ├─ audit.py                    │
  │                               ├─ llm_service.py (risk check)│
  │                               ├─ Analysis...                │
  │                               ├─ Save findings ─────────────►│
  │                               │  (audit_findings table)      │
  │                               ├─ webhook_service (notify)   │
  │                           ◄───┤ 200 OK + findings           │
  │◄───────────────────────────────┤ [{type: "Risk", ...}]      │
  │
  ├─── 4. POST /ask ────────────►│                              │
  │   (question, doc_ids: [...])   │                              │
  │                               ├─ ask.py                      │
  │                               ├─ embedding_service          │
  │                               │  (convert Q to vector)       │
  │                               ├─ Search ChromaDB ───────────►│ (Vector DB)
  │                               │◄─────────────────────────────┤ [similar text]
  │                               ├─ llm_service.py (answer)    │
  │                               ├─ Record in DB ───────────────►│
  │                               │  (query_logs table)          │
  │                           ◄───┤ 200 OK + answer             │
  │◄───────────────────────────────┤ {answer: "...", source: ...}
  │
  └─────────────────────────────────────────────────────────────┘

External System
  │
  │ (Receives webhook notifications)
  │ POST https://your-system.com/notify
  │ {event: "extraction_complete", document_id: "doc-123", ...}
  │
```

---

## 🎓 Learning Path

**If you're new to this project, follow this order:**

```
1. START HERE
   └─ Read: PROJECT_EXPLANATION.md (this file!)
   └─ Understand: What does the system do?

2. UNDERSTAND THE ARCHITECTURE
   └─ Read: app/main.py
   └─ Understand: How is it organized?

3. LEARN EACH COMPONENT
   └─ pdf_service.py     (How PDFs are read)
   └─ llm_service.py     (How ChatGPT is used)
   └─ embedding_service.py (How search works)

4. EXPLORE THE API ENDPOINTS
   └─ Try: http://127.0.0.1:8888/docs
   └─ Test: Each endpoint in Swagger UI

5. SEE IT IN ACTION
   └─ Run: examples.py
   └─ Try: test_api.sh
   └─ Build: Your own integration

6. DEPLOY TO PRODUCTION
   └─ Read: DEPLOYMENT.md
   └─ Choose: Docker, AWS, Heroku, etc.
```

---

## 💡 Key Concepts

### **1. Async/Await**
```python
# Traditional (blocking)
response = requests.get("https://api.openai.com/...")
print(response.text)

# Async (non-blocking) - ours
response = await openai_client.chat.completions.create(...)
print(response.text)
```
**Why it matters:** Can handle 100 requests at once instead of one at a time.

---

### **2. Embeddings & Vector Search**
```
Text: "The payment term is Net 30"
↓ (Embedding Model)
Vector: [0.12, -0.45, 0.89, -0.23, 0.67, ...]
↓ (Store in ChromaDB)
Query: "When should we pay?"
↓ (Embed same way)
Query Vector: [0.10, -0.43, 0.91, -0.25, 0.65, ...]
↓ (Find similar)
Cosine Similarity: 0.98 (99% match!)
```
**Why it matters:** Finds answers without exact keyword match.

---

### **3. Webhooks**
```
When extraction finishes:
  POST https://your-system.com/notify
  {
    event: "extraction_complete",
    document_id: "doc-123",
    fields: {...}
  }
```
**Why it matters:** Real-time notifications to other systems.

---

### **4. Provider Pattern**
```python
# Can switch AI providers without changing code
llm = OpenAIProvider(api_key)  # Uses ChatGPT
# OR
llm = LocalLLMProvider()       # Uses rules/regex (offline)
# OR
llm = AnthropicProvider(api_key)  # Uses Claude

# All have same interface:
await llm.extract_fields(text)
await llm.detect_risks(text)
```
**Why it matters:** Flexibility - switch between AI providers easily.

---

## ✨ Special Features

### **1. Graceful Degradation**
If ChatGPT API is down:
→ Falls back to LocalLLMProvider
→ Uses regex patterns and rules
→ Still works, just less accurate

### **2. Retry Logic**
If webhook delivery fails:
→ Retry 1... wait 1 second
→ Retry 2... wait 2 seconds
→ Retry 3... wait 4 seconds
→ Give up and log error

### **3. Vector Search Fallback**
If ChromaDB unavailable:
→ Uses keyword matching
→ Still works, slower but functional

---

## 🎯 Real-World Use Cases

### **Scenario 1: Legal Team Review**
```
Monday morning: Upload 50 supplier agreements
2 minutes later: All extracted and audited
Dashboard shows: Contracts with critical risks
Action: Review only high-risk ones
Result: 80% time saved!
```

### **Scenario 2: Contract Analysis**
```
Finance team asks: "Which contracts have auto-renewal?"
System searches all uploaded contracts
Returns: 5 contracts with auto-renewal
Shows: Exact clause from each
Action: Negotiate renewal terms
```

### **Scenario 3: Compliance Checking**
```
Risk officer uploads government contracts
System detects: Indemnification issues
Sends webhook to ticketing system
Ticket created: "Review indemnification clause"
Notification: Sent to compliance team
Action: Address issue before signing
```

---

## 🚀 Next Steps

1. **Access the API**: http://127.0.0.1:8888/docs
2. **Try an example**: Read `examples.py`
3. **Upload a contract**: Test the `/ingest` endpoint
4. **Extract fields**: Test the `/extract` endpoint
5. **Ask questions**: Test the `/ask` endpoint
6. **Integrate**: Use `client.py` in your code

---

**You now understand the complete Contract Intelligence API!** 🎉
