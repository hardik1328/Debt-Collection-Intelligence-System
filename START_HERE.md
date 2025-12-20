# 🚀 START HERE - Getting Started Guide

## Welcome to Contract Intelligence API!

This is a **production-ready** system for analyzing contracts using AI. You can upload PDFs, extract key information, ask questions, and identify risky clauses.

---

## ⚡ 30-Second Setup

### Option 1: Docker (Recommended - Easiest)
```bash
cd contract-intelligence-api
docker-compose up -d

# That's it! API is ready at: http://localhost:8000/docs
```

### Option 2: Local Python
```bash
cd contract-intelligence-api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# API ready at: http://localhost:8000/docs
```

---

## 🧪 Try It (3 Easy Steps)

### Step 1: Check It's Running
```bash
curl http://localhost:8000/admin/healthz
# Should return: {"status": "healthy", ...}
```

### Step 2: Upload a Contract
```bash
curl -X POST http://localhost:8000/ingest \
  -F "files=@sample_contract.pdf"
# Returns: {"document_ids": ["uuid"], ...}
# Save the uuid for next steps!
```

### Step 3: Ask a Question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the payment term?",
    "document_ids": ["uuid-from-step-2"]
  }'
# Returns: {"answer": "...", "citations": [...]}
```

---

## 📊 What You Can Do

### 1. Upload PDFs
```bash
# Single file
curl -F "files=@contract.pdf" http://localhost:8000/ingest

# Multiple files
curl -F "files=@contract1.pdf" -F "files=@contract2.pdf" http://localhost:8000/ingest
```

### 2. Extract Contract Fields
```bash
curl -X POST "http://localhost:8000/extract?document_id=uuid"
# Returns: parties, dates, payment terms, liability caps, etc.
```

### 3. Ask Questions About Contracts
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the governing law?"}'
```

### 4. Run Risk Audit
```bash
curl -X POST "http://localhost:8000/audit?document_id=uuid"
# Detects risky clauses and rates severity
```

### 5. Stream Real-Time Responses
```bash
curl "http://localhost:8000/ask/stream?question=What%20are%20the%20key%20terms?"
# Streams token-by-token
```

---

## 🎯 Try the Interactive API Docs

**Open your browser:** http://localhost:8000/docs

You can:
- ✅ See all endpoints
- ✅ Try requests directly
- ✅ View response examples
- ✅ Test without writing code

---

## 🐛 If Something Doesn't Work

### Check if it's running
```bash
curl http://localhost:8000/admin/healthz
```

### View logs
```bash
docker-compose logs -f contract-api
```

### Reset everything
```bash
docker-compose down
docker-compose up -d
```

### Common issues
- **Port 8000 in use**: Close other apps or change port in docker-compose.yml
- **PDF not extracting**: Make sure it's not password-protected
- **Slow responses**: Use local LLM in .env instead of OpenAI

---

## 📚 Documentation

| Document | For |
|----------|-----|
| **[QUICKSTART.md](QUICKSTART.md)** | Quick reference & tips |
| **[README.md](README.md)** | Full feature guide |
| **[API_SPEC.md](API_SPEC.md)** | Detailed API reference |
| **[DEPLOYMENT.md](DEPLOYMENT.md)** | Production deployment |
| **[examples.py](examples.py)** | Code examples |
| **[client.py](client.py)** | Python SDK |

---

## 🔗 Sample Contracts to Test

Need test PDFs? Download here:
1. **NDA**: https://www.contractstandards.com/nda
2. **Service Agreement**: https://www.contractstandards.com/msa
3. **Terms of Service**: https://github.com/github/site-policy
4. **License**: https://opensource.org/licenses/MPL-2.0

See [RESOURCES.md](RESOURCES.md) for more.

---

## 💻 Use Python (Easy Integration)

```python
from client import ContractIntelligenceAPI

api = ContractIntelligenceAPI("http://localhost:8000")

# Upload
doc_ids, docs = api.ingest(["contract.pdf"])
print(f"Uploaded: {doc_ids}")

# Extract
fields = api.extract_fields(doc_ids[0])
print(f"Parties: {fields['parties']}")

# Ask
answer = api.ask("What is the payment term?", doc_ids)
print(f"Answer: {answer['answer']}")

# Audit
audit = api.audit(doc_ids[0])
print(f"Risks found: {len(audit['findings'])}")
```

---

## 🎓 Learning Path

1. **Right Now**: Read this file (you are here!)
2. **Next 5 mins**: Try the interactive API docs at /docs
3. **Next 15 mins**: Run the quick test commands above
4. **Next hour**: Read [QUICKSTART.md](QUICKSTART.md)
5. **Next few hours**: Review [README.md](README.md) and [API_SPEC.md](API_SPEC.md)
6. **Production**: Follow [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🆘 Quick Help

### API isn't responding
```bash
# Check health
curl http://localhost:8000/admin/healthz

# View system status
curl http://localhost:8000/admin/status | jq
```

### Need to see all endpoints
```bash
curl http://localhost:8000/openapi.json | jq
# Or visit: http://localhost:8000/docs
```

### Want to test with real data
```bash
# See examples.py for real-world usage patterns
python examples.py | head -20
```

### Having PDF issues
- Must be a valid PDF file
- Cannot be password-protected
- Size limit: 50MB (configurable)
- Try different PDFs to test

---

## 🚀 Next Level Features

### Webhooks (Async Notifications)
```bash
curl -X POST http://localhost:8000/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-webhook-url.com/events",
    "events": ["extraction_complete", "audit_complete"]
  }'
```

### Streaming Responses (Real-time)
```bash
# Get token-by-token streaming
curl "http://localhost:8000/ask/stream?question=What%20is%20this%20agreement%3F"
```

### Batch Processing
```python
# Process multiple contracts
import glob
for pdf in glob.glob("contracts/*.pdf"):
    result = api.ingest([pdf])
    audit = api.audit(result[0][0])
    print(f"{pdf}: {audit['summary']}")
```

---

## 🎯 Common Workflows

### Workflow 1: Quick Risk Check
```bash
# 1. Upload contract
DOC_ID=$(curl -s -F "files=@contract.pdf" \
  http://localhost:8000/ingest | jq -r '.document_ids[0]')

# 2. Run audit
curl -X POST "http://localhost:8000/audit?document_id=$DOC_ID" | jq '.findings'
```

### Workflow 2: Extract & Compare
```bash
# 1. Upload contracts
curl -F "files=@contract1.pdf" -F "files=@contract2.pdf" \
  http://localhost:8000/ingest

# 2. Extract from both
for doc_id in uuid1 uuid2; do
  curl -X POST "http://localhost:8000/extract?document_id=$doc_id"
done

# 3. Compare results (Python)
import json
# ... load and compare extractions
```

### Workflow 3: Answer Multiple Questions
```python
questions = [
  "What is the payment term?",
  "Who are the parties?",
  "What happens if I terminate early?",
  "What is the liability cap?"
]

for q in questions:
    answer = api.ask(q, [doc_id])
    print(f"Q: {q}\nA: {answer['answer']}\n")
```

---

## ✨ Pro Tips

1. **Speed**: Upload multiple PDFs at once
2. **Caching**: Extraction results are cached
3. **Precision**: Be specific in questions for better answers
4. **Audits**: Check both findings and summary
5. **Streaming**: Use /ask/stream for large responses
6. **Webhooks**: Register for async notifications
7. **History**: Check /ask/queries for previous questions
8. **Metrics**: Monitor /admin/metrics for usage stats

---

## 🎉 You're All Set!

You now have a **production-ready** Contract Intelligence system running locally!

### Next Steps:
1. ✅ API is running
2. ✅ Try the /docs interface
3. ✅ Upload a test PDF
4. ✅ Run an audit
5. ✅ Ask questions
6. ✅ Explore the code
7. ✅ Deploy to production when ready

### Need Help?
- Check [QUICKSTART.md](QUICKSTART.md) for quick reference
- Read [README.md](README.md) for full guide
- Review [examples.py](examples.py) for code samples
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup

---

## 🚀 Deploy to Production

When ready to go live:
```bash
# Follow DEPLOYMENT.md for your platform
# Options: Docker, Kubernetes, AWS ECS, Heroku, DigitalOcean
```

---

**Questions? Visit the docs at http://localhost:8000/docs**

**Happy contract analyzing! 🎊**
