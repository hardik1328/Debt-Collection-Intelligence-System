# 📚 File-by-File Summary (Quick Reference)

## 🚀 Entry Point

**`main.py` at root** OR **`app/main.py`**
- Starts the FastAPI web server
- Creates database tables
- Registers all API routes
- Sets up middleware (CORS)
- Can run with: `python main.py` or `uvicorn app.main:app --host 127.0.0.1 --port 8888`

---

## 📂 Core Application (`app/`)

### **Configuration (`app/core/`)**

| File | Purpose | Key Features |
|------|---------|--------------|
| `config.py` | Read settings from `.env` file | API title, LLM provider, database URL, API keys |
| `logger.py` | Setup logging | Timestamps, log levels (INFO, ERROR, WARNING) |

---

### **Data Models (`app/models/`)**

| File | Purpose | Contains |
|------|---------|----------|
| `database.py` | Define database structure | 5 tables: contracts, extracted_fields, audit_findings, query_logs, webhook_events |
| `schemas.py` | Define request/response formats | Pydantic models for validation |

---

### **Business Logic (`app/services/`)**

| File | Purpose | Main Classes |
|------|---------|--------------|
| `pdf_service.py` | Extract text from PDFs | `PDFExtractor`, `PDFMetadata` |
| `llm_service.py` | AI integration | `OpenAIProvider`, `LocalLLMProvider`, `LLMProvider` (base) |
| `embedding_service.py` | Vector search/embeddings | `EmbeddingService`, `VectorStore` |
| `webhook_service.py` | Send event notifications | `WebhookManager` |

---

### **API Endpoints (`app/api/`)**

| File | Routes | What It Does |
|------|--------|-------------|
| `ingest.py` | POST/GET/DELETE `/ingest` | Upload PDFs, list docs, delete docs |
| `extract.py` | POST/GET `/extract` | Extract structured fields from contracts |
| `ask.py` | POST/GET `/ask` | Q&A system with streaming support |
| `audit.py` | POST/GET `/audit` | Detect risks and red flags |
| `admin.py` | GET/POST `/admin` | Health checks, metrics, system status |
| `webhooks.py` | POST/GET/DELETE `/webhooks` | Register event callbacks |

---

## 📦 Supporting Files

### **Root Level**

| File | Purpose |
|------|---------|
| `README.md` | Quick start guide |
| `API_SPEC.md` | Complete API documentation |
| `DEPLOYMENT.md` | How to deploy to cloud |
| `PROJECT_SUMMARY.md` | Technical overview |
| `QUICKSTART.md` | 30-second setup |
| `PROJECT_EXPLANATION.md` | 📍 Detailed explanation (created) |
| `ARCHITECTURE_GUIDE.md` | 📍 Visual diagrams (created) |
| `requirements.txt` | All Python dependencies |
| `requirements_minimal.txt` | Core dependencies only |
| `.env.example` | Configuration template |
| `client.py` | Python SDK for easy integration |
| `examples.py` | Code examples and workflows |
| `utils.py` | Development utilities |
| `test_api.sh` | Bash curl tests |
| `docker-compose.yml` | Docker configuration |
| `Dockerfile` | Docker image definition |

---

## 🔄 How the Files Work Together

```
User sends HTTP Request
     ↓
app/main.py (routes to correct handler)
     ↓
app/api/[endpoint].py (validates input)
     ↓
app/services/[service].py (business logic)
     ↓
app/models/database.py & schemas.py (data handling)
     ↓
data/db/contracts.db (SQLite database)
     ↓
Response sent back to user
```

---

## 📊 Which Files to Look At For What

### **"How do I upload a PDF?"**
→ Look at: `app/api/ingest.py`

### **"How does it extract contract information?"**
→ Look at: `app/services/llm_service.py` + `app/api/extract.py`

### **"How does the Q&A work?"**
→ Look at: `app/services/embedding_service.py` + `app/api/ask.py`

### **"How are risks detected?"**
→ Look at: `app/services/llm_service.py` + `app/api/audit.py`

### **"Where is data stored?"**
→ Look at: `app/models/database.py` + `data/db/contracts.db`

### **"How do webhooks work?"**
→ Look at: `app/services/webhook_service.py` + `app/api/webhooks.py`

### **"How do I integrate this into my app?"**
→ Look at: `client.py` + `examples.py`

### **"How do I deploy it?"**
→ Look at: `DEPLOYMENT.md` + `docker-compose.yml`

### **"What settings can I change?"**
→ Look at: `app/core/config.py` + `.env.example`

---

## 🎯 The 4-File Core

If you want to understand 80% of what's happening, read these 4 files:

1. **`app/main.py`** - The orchestrator
2. **`app/services/pdf_service.py`** - How PDFs are read
3. **`app/services/llm_service.py`** - How AI analyzes contracts
4. **`app/models/database.py`** - How data is stored

---

## 📈 Project Statistics

| Metric | Count |
|--------|-------|
| Python Files | 21 |
| API Endpoints | 21 |
| Database Tables | 5 |
| Services | 4 |
| Documentation Files | 11 |
| Total Lines of Code | 3500+ |
| Dependencies | 25+ |

---

## ✅ Health Check

To verify everything is working:

```bash
# 1. Check if server is running
curl http://127.0.0.1:8888/

# 2. Check health
curl http://127.0.0.1:8888/admin/healthz

# 3. See docs
open http://127.0.0.1:8888/docs

# 4. List uploaded documents
curl http://127.0.0.1:8888/ingest/documents
```

---

## 🎓 Learning Resources

- **START**: PROJECT_EXPLANATION.md (detailed walkthrough)
- **VISUAL**: ARCHITECTURE_GUIDE.md (diagrams and flow)
- **QUICK**: QUICKSTART.md (30-second setup)
- **HANDS-ON**: examples.py (code examples)
- **API**: http://127.0.0.1:8888/docs (interactive Swagger UI)

---

## 🚀 You're All Set!

The system is:
✅ Running on http://127.0.0.1:8888
✅ Connected to SQLite database
✅ Ready to upload contracts
✅ Ready to extract information
✅ Ready to answer questions
✅ Ready to detect risks

Start by uploading a PDF and exploring! 🎉
