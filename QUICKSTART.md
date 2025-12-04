# Quick Start Guide

## 🚀 30-Second Setup

### Option 1: Docker (Recommended)

```bash
cd contract-intelligence-api
docker-compose up -d
# API ready at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Option 2: Local Python

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
# API ready at http://localhost:8000
```

---

## 📝 First Steps

### 1. Check Health
```bash
curl http://localhost:8000/admin/healthz
```

### 2. Upload a Contract
```bash
curl -X POST http://localhost:8000/ingest \
  -F "files=@your_contract.pdf"
# Returns: { "document_ids": ["uuid"], "documents": [...] }
```

### 3. Extract Fields
```bash
curl -X POST http://localhost:8000/extract?document_id=<uuid>
# Returns: { "parties": [...], "effective_date": "...", ... }
```

### 4. Ask Questions
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the payment term?",
    "document_ids": ["<uuid>"]
  }'
# Returns: { "answer": "...", "citations": [...] }
```

### 5. Run Audit
```bash
curl -X POST http://localhost:8000/audit?document_id=<uuid>
# Returns: { "findings": [...], "summary": "..." }
```

---

## 🔧 Configuration

### LLM Provider

**Local (default, no setup needed)**
```
LLM_PROVIDER=local
```

**OpenAI**
```
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4-turbo-preview
```

Edit `.env` and restart.

---

## 📊 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/ingest` | POST | Upload PDFs |
| `/extract` | POST | Extract fields |
| `/ask` | POST | Ask questions |
| `/ask/stream` | GET | Stream responses |
| `/audit` | POST | Run risk audit |
| `/admin/healthz` | GET | Health check |
| `/admin/metrics` | GET | System metrics |
| `/docs` | GET | Swagger UI |

---

## 🐳 Docker Commands

```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild
docker-compose build --no-cache

# Shell into container
docker-compose exec contract-api bash
```

---

## 🧪 Testing

### Using Python Requests
```python
import requests

response = requests.post(
    "http://localhost:8000/ingest",
    files={"files": open("contract.pdf", "rb")}
)
doc_id = response.json()["document_ids"][0]

# Extract
result = requests.post(f"http://localhost:8000/extract?document_id={doc_id}")
print(result.json())
```

### Using the SDK
```python
from client import ContractIntelligenceAPI

api = ContractIntelligenceAPI()
doc_ids, docs = api.ingest(["contract.pdf"])
fields = api.extract_fields(doc_ids[0])
answer = api.ask("What is the payment term?", doc_ids)
audit = api.audit(doc_ids[0])
```

---

## 📚 Interactive API Docs

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Try requests directly from your browser!

---

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Find process using 8000
lsof -i :8000
# Kill it
kill -9 <PID>
```

### Database Lock
```bash
# Remove lock files
rm data/db/*.db-*
```

### Dependencies Issue
```bash
pip install --upgrade -r requirements.txt
```

### PDF Not Extracting
- Ensure PDF is not password-protected
- Try different PDF files
- Check logs: `docker-compose logs`

---

## 🚀 Next Steps

1. Read full [README.md](README.md)
2. Check [API_SPEC.md](API_SPEC.md) for all endpoints
3. Review [examples.py](examples.py) for code samples
4. See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

---

## 📞 Support

- Check logs: `docker-compose logs -f`
- API status: `http://localhost:8000/admin/status`
- Metrics: `http://localhost:8000/admin/metrics`

---

## 💡 Pro Tips

1. **Batch Processing**: Upload multiple PDFs at once to `/ingest`
2. **Caching**: Extracted fields are cached in the database
3. **Webhooks**: Register webhooks for async notifications
4. **Streaming**: Use `/ask/stream` for real-time responses
5. **Audit Filtering**: Get specific severity findings with `/audit/findings?severity=critical`

---

## 🎯 Common Tasks

### Upload 10 PDFs and audit all
```bash
for i in {1..10}; do
  curl -F "files=@contract_$i.pdf" http://localhost:8000/ingest
done

# Get all documents and audit
curl http://localhost:8000/ingest/documents | jq '.[] | .document_id' | \
  xargs -I {} curl -X POST http://localhost:8000/audit?document_id={}
```

### Stream real-time answers
```bash
curl "http://localhost:8000/ask/stream?question=What%20are%20the%20key%20terms?"
```

### Get risk summary
```bash
curl http://localhost:8000/audit/summary/<document_id> | jq
```

### Export metrics
```bash
curl http://localhost:8000/admin/metrics | jq > metrics.json
```

---

Happy contract analyzing! 🎉
