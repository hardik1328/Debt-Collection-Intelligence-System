# 📋 Contract Intelligence API - Complete Project Explanation

## 🎯 What Is This Project?

This is a **Smart Contract Analysis System** that helps you:
1. **Upload PDF contracts** (agreements, terms & conditions, legal documents)
2. **Automatically extract important information** (parties, dates, payment terms, liability caps, etc.)
3. **Ask questions** about the contracts and get answers
4. **Detect risks and red flags** in contracts (unusual clauses, unfair terms, etc.)
5. **Send webhooks** to other systems when analysis is complete

**Real-World Example:**
- You upload 10 supplier agreements
- System extracts key terms from each
- You ask "Which contracts have auto-renewal?" 
- System finds risky auto-renewal clauses with <30 days notice
- Results sent to your team via webhooks

---

## 🏗️ Project Architecture

```
contract-intelligence-api/
├── app/                          # Main application code
│   ├── main.py                   # Entry point (starts everything)
│   ├── api/                      # API endpoints (what users call)
│   │   ├── ingest.py            # Upload PDFs
│   │   ├── extract.py           # Extract structured fields
│   │   ├── ask.py               # Q&A endpoint
│   │   ├── audit.py             # Risk detection
│   │   ├── admin.py             # Health/metrics
│   │   └── webhooks.py          # Event callbacks
│   ├── services/                 # Business logic (how things work)
│   │   ├── pdf_service.py       # Extract text from PDFs
│   │   ├── llm_service.py       # AI/ChatGPT integration
│   │   ├── embedding_service.py # Vector search
│   │   └── webhook_service.py   # Send events
│   ├── models/                   # Data structures
│   │   ├── database.py          # Database tables
│   │   └── schemas.py           # Request/response formats
│   └── core/                     # Configuration
│       ├── config.py            # Settings
│       └── logger.py            # Logging
├── data/                         # Data storage
│   ├── uploads/                 # Uploaded PDFs
│   ├── db/                       # SQLite database
│   └── chroma/                  # Vector search index
├── tests/                        # Tests
├── README.md                     # Quick start guide
├── requirements.txt              # Python dependencies
└── docker-compose.yml            # Docker setup
```

---

## 📁 File-by-File Explanation

### **Core Application Files**

#### `app/main.py` 🚀
**What it does:** Starts the entire application
- Initializes FastAPI (web framework)
- Creates database tables
- Connects all API endpoints
- Sets up logging

**Key code:**
```python
app = FastAPI(title="Contract Intelligence API")
app.include_router(ingest.router)    # Adds PDF upload
app.include_router(extract.router)   # Adds field extraction
app.include_router(ask.router)       # Adds Q&A
```

**Result:** When you run the app, this starts the web server on http://localhost:8888

---

### **API Endpoints (app/api/)**

#### `app/api/ingest.py` 📤
**What it does:** Handles PDF uploads
- Users upload 1 or more PDF files
- Files are saved to disk
- Text is extracted and stored in database
- Returns document IDs for later use

**Endpoints:**
- `POST /ingest` - Upload PDFs
- `GET /ingest/documents` - List uploaded documents
- `GET /ingest/documents/{id}` - Get one document's details
- `DELETE /ingest/documents/{id}` - Delete a document

**Example:**
```bash
# Upload a contract
curl -X POST "http://localhost:8888/ingest" -F "files=@contract.pdf"

# Returns:
{
  "documents": [{
    "id": "doc-123",
    "filename": "contract.pdf",
    "pages": 10,
    "upload_date": "2025-12-04"
  }]
}
```

---

#### `app/api/extract.py` 🔍
**What it does:** Extracts structured information from contracts
- Takes uploaded document ID
- Uses AI (ChatGPT or local LLM) to extract fields
- Saves extracted data to database
- Returns organized information

**Endpoints:**
- `POST /extract?document_id=doc-123` - Extract fields from document
- `GET /extract/fields/{document_id}` - Get previously extracted fields

**Fields extracted:**
```
- parties (company names)
- effective_date (when contract starts)
- term (how long it lasts)
- governing_law (which laws apply)
- payment_terms (when to pay)
- auto_renewal (does it renew automatically?)
- liability_cap (max amount company can be sued for)
- signatories (who signed it)
```

**Example:**
```bash
curl -X POST "http://localhost:8888/extract?document_id=doc-123"

# Returns:
{
  "parties": ["Company A Inc", "Company B Ltd"],
  "effective_date": "2025-01-01",
  "term": "3 years",
  "payment_terms": "Net 30",
  "liability_cap": {"amount": 1000000, "currency": "USD"}
}
```

---

#### `app/api/ask.py` ❓
**What it does:** Q&A system - ask questions about contracts
- You ask a question
- System searches through contract text
- Uses AI to find and answer from the contract
- Returns answer with source/citation

**Endpoints:**
- `POST /ask` - Ask a question
- `GET /ask/stream` - Stream answer in real-time
- `GET /ask/queries` - See question history

**How it works:**
1. Takes your question: "What is the termination clause?"
2. Converts question to numbers (embeddings)
3. Searches contract using vector search
4. Finds relevant paragraphs
5. Uses AI to answer based on those paragraphs
6. Returns answer with source location

**Example:**
```bash
curl -X POST "http://localhost:8888/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the payment term?",
    "document_ids": ["doc-123"],
    "top_k": 5
  }'

# Returns:
{
  "answer": "The payment term is Net 30, meaning payment is due within 30 days of invoice.",
  "source": "Page 3, Section 4.1",
  "confidence": 0.92
}
```

---

#### `app/api/audit.py` ⚠️
**What it does:** Finds risky clauses in contracts
- Analyzes contract for red flags
- Identifies problematic terms
- Rates severity (Critical, High, Medium, Low)
- Provides recommendations

**Endpoints:**
- `POST /audit?document_id=doc-123` - Audit a document
- `GET /audit/findings/{document_id}` - Get findings
- `GET /audit/summary/{document_id}` - Get risk summary

**Types of risks detected:**
- Auto-renewal with less than 30 days notice
- Unlimited liability
- Broad indemnification clauses
- Unfavorable payment terms
- Restricted termination rights
- Confidentiality issues

**Example:**
```bash
curl -X POST "http://localhost:8888/audit?document_id=doc-123"

# Returns:
{
  "findings": [
    {
      "type": "Auto-renewal",
      "severity": "HIGH",
      "description": "Contract auto-renews with only 10 days notice",
      "recommendation": "Negotiate for 90 days notice period"
    },
    {
      "type": "Liability",
      "severity": "CRITICAL",
      "description": "No liability cap found",
      "recommendation": "Add liability limitation clause"
    }
  ]
}
```

---

#### `app/api/admin.py` 📊
**What it does:** System health and monitoring
- Check if API is running
- Get performance metrics
- System status
- Reset data for testing

**Endpoints:**
- `GET /admin/healthz` - Health check
- `GET /admin/metrics` - Performance stats
- `GET /admin/status` - System status
- `POST /admin/reset` - Clear all data

**Example:**
```bash
curl "http://localhost:8888/admin/healthz"

# Returns:
{
  "status": "healthy",
  "timestamp": "2025-12-04T17:04:18",
  "uptime_seconds": 120
}
```

---

#### `app/api/webhooks.py` 🔗
**What it does:** Event notifications
- Register webhooks to receive notifications
- Triggered when extraction or audit completes
- Sends data to external systems
- Retry logic if delivery fails

**Endpoints:**
- `POST /webhooks/register` - Register a webhook
- `GET /webhooks/list` - See registered webhooks
- `DELETE /webhooks/{id}` - Remove webhook

**Example:**
```bash
# Register webhook
curl -X POST "http://localhost:8888/webhooks/register" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-system.com/notify",
    "events": ["extraction_complete", "audit_complete"]
  }'

# When extraction finishes, we POST to your URL:
POST https://your-system.com/notify
{
  "event": "extraction_complete",
  "document_id": "doc-123",
  "fields": {...}
}
```

---

### **Services (app/services/)**

#### `app/services/pdf_service.py` 📄
**What it does:** Extracts text from PDF files
- Uses `pdfplumber` library (better text extraction)
- Reads each page
- Combines all pages into one text
- Returns full text + page count

**Classes:**
- `PDFExtractor` - Extract text from PDF
- `PDFMetadata` - Get PDF metadata (title, author, etc.)

**Example:**
```python
pdf = PDFExtractor()
text, pages = pdf.extract_text("contract.pdf")
# Returns: text = "Company A Inc. agrees...", pages = 10
```

---

#### `app/services/llm_service.py` 🤖
**What it does:** AI/ChatGPT integration
- Connects to OpenAI's ChatGPT or local AI
- Extracts fields from contract text
- Answers questions
- Detects risks

**Classes:**
- `LLMProvider` - Base interface
- `OpenAIProvider` - Uses OpenAI API
- `LocalLLMProvider` - Uses local rules/regex (fallback)

**How it works:**
```python
llm = OpenAIProvider(api_key="sk-...")

# Extract fields
fields = await llm.extract_fields("Company A Inc agrees to...")
# Returns: {parties: ["A", "B"], term: "3 years", ...}

# Answer question
answer = await llm.answer_question(
  question="What is payment term?",
  context="Company A Inc. contract text..."
)
# Returns: "Net 30"

# Detect risks
risks = await llm.detect_risks("contract text...")
# Returns: [{type: "Auto-renewal", severity: "HIGH"}, ...]
```

---

#### `app/services/embedding_service.py` 🔤➡️🔢
**What it does:** Vector search (semantic search)
- Converts text to "embeddings" (numbers that represent meaning)
- Stores in vector database (ChromaDB)
- Finds similar paragraphs when you ask a question

**Classes:**
- `EmbeddingService` - Convert text to embeddings
- `VectorStore` - Store and search embeddings

**Why it matters:**
When you ask "payment terms?", it doesn't just search for the word "payment".
It finds semantically similar text, so it finds "When should we be paid?" too.

**Example:**
```python
embeddings = EmbeddingService()
vector_store = VectorStore()

# Store contract text
vector_store.add_text("Company A will pay Net 30")

# Search for similar
results = vector_store.search("payment")
# Returns: ["Company A will pay Net 30", ...]
```

---

#### `app/services/webhook_service.py` 🔔
**What it does:** Sends event notifications
- Triggers when extraction/audit completes
- Sends data to registered webhook URLs
- Retries if delivery fails
- Logs all attempts

**Classes:**
- `WebhookManager` - Register and trigger webhooks

**Example:**
```python
manager = WebhookManager(db)

# When extraction finishes
await manager.emit_event(
  event="extraction_complete",
  document_id="doc-123",
  payload={fields: {...}}
)
# Sends POST to all registered webhooks
```

---

### **Data Models (app/models/)**

#### `app/models/database.py` 💾
**What it does:** Database structure (what data is stored)
- Creates SQLite database
- Defines 5 tables

**Tables:**

1. **contracts** - Uploaded PDF documents
```
- id: unique identifier
- filename: original filename
- raw_text: extracted text from PDF
- pages: number of pages
- upload_date: when uploaded
```

2. **extracted_fields** - Extracted information from contracts
```
- id: unique identifier
- contract_id: which contract
- parties, effective_date, term, payment_terms, etc.
- extraction_date: when extracted
```

3. **audit_findings** - Risk findings
```
- id: unique identifier
- contract_id: which contract
- finding_type: what risk (e.g., "Auto-renewal")
- severity: how bad (CRITICAL, HIGH, MEDIUM, LOW)
- description: what's the problem
```

4. **query_logs** - Q&A history
```
- id: unique identifier
- question: what was asked
- answer: what was returned
- created_date: when asked
```

5. **webhook_events** - Events sent to webhooks
```
- id: unique identifier
- webhook_url: where sent
- event_type: what happened
- status: success/failed
```

**How to access:**
```python
from app.models.database import Contract, ExtractedFields
# Use these to query the database
```

---

#### `app/models/schemas.py` 📋
**What it does:** Request/response formats (what data comes in/out)
- Defines validation rules
- Specifies what fields are required
- Formats API responses

**Key schemas:**
- `IngestResponse` - Response after uploading PDFs
- `ContractFields` - Extracted fields response
- `AskRequest` - Question input
- `AskResponse` - Answer output
- `AuditResponse` - Risk findings output
- `HealthResponse` - Health check output

**Example:**
```python
class AskRequest(BaseModel):
    question: str  # User must provide this
    document_ids: List[str]  # Which contracts to search
    top_k: int = 5  # How many results

# When you POST to /ask, it must match this format
```

---

### **Configuration (app/core/)**

#### `app/core/config.py` ⚙️
**What it does:** Settings and configuration
- Reads from `.env` file
- Sets defaults
- Controls behavior

**Key settings:**
- `LLM_PROVIDER` - Which AI to use (openai, anthropic, local)
- `OPENAI_API_KEY` - Your ChatGPT API key
- `DATABASE_URL` - Where to store data
- `MAX_FILE_SIZE` - Max PDF size
- `VECTOR_STORE_TYPE` - ChromaDB or local search

**Example .env file:**
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=sqlite:///./data/db/contracts.db
MAX_FILE_SIZE=50
```

---

#### `app/core/logger.py` 📝
**What it does:** Logging and debugging
- Records all events
- Helps troubleshoot issues
- Shows timestamps and levels (INFO, ERROR, WARNING)

**Example log output:**
```
2025-12-04 17:04:18,306 - app.core.logger - INFO - Starting Contract Intelligence API v1.0.0
2025-12-04 17:04:18,306 - app.core.logger - INFO - LLM Provider: openai
```

---

## 📦 Supporting Files

### `requirements.txt` 📚
**What it contains:** List of Python libraries needed
- `fastapi` - Web framework
- `uvicorn` - Web server
- `pydantic` - Data validation
- `sqlalchemy` - Database ORM
- `pypdf`, `pdfplumber` - PDF reading
- `openai` - ChatGPT API
- `chromadb` - Vector search database
- And many more...

**Usage:**
```bash
pip install -r requirements.txt  # Install all dependencies
```

---

### `docker-compose.yml` 🐳
**What it does:** Runs the app in Docker (containerization)
- Defines how to run the app in a container
- Sets environment variables
- Maps ports
- Mounts volumes for data persistence

**Usage:**
```bash
docker-compose up -d  # Start the app
docker-compose down   # Stop the app
```

---

### `.env.example` 📄
**What it is:** Template for configuration
- Shows what settings exist
- Provides default values
- Users copy this to `.env` and customize

---

### `README.md` 📖
**What it contains:** Quick start guide
- How to install
- How to run
- Example API calls

---

### `examples.py` 💡
**What it contains:** Code examples
- Show how to use the API
- Common workflows
- Integration patterns

---

### `client.py` 🐍
**What it is:** Python SDK/wrapper
- Makes it easier to use the API from Python
- Instead of writing HTTP requests manually, you can do:

```python
from client import ContractIntelligenceClient

client = ContractIntelligenceClient("http://localhost:8888")

# Upload
docs = await client.ingest(["contract.pdf"])

# Extract
fields = await client.extract(docs[0])

# Ask
answer = await client.ask("What is payment term?", [docs[0]])
```

---

## 🔄 Workflow Example: Start to Finish

### **Scenario: Upload a supplier contract and analyze it**

**Step 1: Upload (ingest.py)**
```bash
curl -X POST "http://localhost:8888/ingest" \
  -F "files=@supplier-agreement.pdf"
```
↓
- File saved to `data/uploads/`
- Text extracted by `pdf_service.py`
- Stored in `contracts` database table
- Returns document ID: `doc-abc123`

**Step 2: Extract Fields (extract.py)**
```bash
curl -X POST "http://localhost:8888/extract?document_id=doc-abc123"
```
↓
- `llm_service.py` reads contract text
- Calls ChatGPT to extract fields
- Saves to `extracted_fields` table
- Returns: parties, dates, payment terms, etc.

**Step 3: Audit for Risks (audit.py)**
```bash
curl -X POST "http://localhost:8888/audit?document_id=doc-abc123"
```
↓
- `llm_service.py` analyzes for risks
- Checks for red flags
- Saves to `audit_findings` table
- Returns: severity, description, recommendations

**Step 4: Ask Questions (ask.py)**
```bash
curl -X POST "http://localhost:8888/ask" \
  -d '{
    "question": "What if we want to terminate early?",
    "document_ids": ["doc-abc123"]
  }'
```
↓
- `embedding_service.py` converts question to vector
- Searches for similar paragraphs
- `llm_service.py` extracts answer
- Returns: answer with source location

**Step 5: Webhook Notification (webhooks.py)**
- If webhooks registered, sends:
```json
{
  "event": "extraction_complete",
  "document_id": "doc-abc123",
  "fields": {...}
}
```

---

## 🎯 Summary

### **In Simple Terms:**

1. **Upload PDFs** → `ingest.py` saves them
2. **Extract Info** → `extract.py` + `llm_service.py` pull out key data
3. **Find Risks** → `audit.py` + `llm_service.py` identify red flags
4. **Ask Questions** → `ask.py` + `embedding_service.py` + `llm_service.py` answer
5. **Get Notifications** → `webhooks.py` sends updates to external systems

### **Technologies Used:**

- **FastAPI** - Web framework (like Flask but faster)
- **SQLAlchemy** - Database ORM (makes database easy)
- **SQLite** - Local database (no setup needed)
- **OpenAI** - AI/ChatGPT (for smart analysis)
- **ChromaDB** - Vector database (for smart search)
- **pdfplumber** - Extract text from PDFs

### **The "Magic" Happens In:**

1. **PDF Extraction** - Reading PDFs reliably
2. **AI Analysis** - Using ChatGPT to understand contracts
3. **Vector Search** - Finding relevant sections quickly
4. **Risk Detection** - Identifying problematic clauses

---

## 📊 How Data Flows

```
PDF File
   ↓
PDF Service (reads text)
   ↓
Database (stores raw text)
   ↓
LLM Service (ChatGPT analyzes)
   ↓
Database (stores extracted fields & risks)
   ↓
Embedding Service (converts to searchable vectors)
   ↓
Vector Database (ChromaDB for fast search)
   ↓
When user asks question:
   → Embedding Service (convert question to vector)
   → Search Vector Database (find similar sections)
   → LLM Service (extract answer)
   → Return to user
   ↓
Webhook Service (notify external systems)
```

---

## 🚀 How to Use It

### **Running the API:**
```bash
cd contract-intelligence-api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8888
```

Visit: **http://127.0.0.1:8888/docs** to see interactive documentation

### **Basic Workflow:**
```bash
# 1. Upload
curl -X POST "http://127.0.0.1:8888/ingest" -F "files=@contract.pdf"

# 2. Extract fields
curl -X POST "http://127.0.0.1:8888/extract?document_id=<ID>"

# 3. Audit risks
curl -X POST "http://127.0.0.1:8888/audit?document_id=<ID>"

# 4. Ask question
curl -X POST "http://127.0.0.1:8888/ask" -d '{"question":"...","document_ids":["<ID>"]}'
```

---

## ✅ What You've Got

✅ Complete contract analysis system
✅ 21 API endpoints ready to use
✅ SQLite database (zero setup)
✅ ChatGPT integration (smart AI analysis)
✅ Vector search (semantic understanding)
✅ Risk detection (identify red flags)
✅ Q&A system (ask about contracts)
✅ Webhooks (notify other systems)
✅ Docker support (easy deployment)
✅ Full documentation (quick start guides)

**The system is production-ready and running!** 🎉
