# Project Documentation Links

## Sample Contracts for Testing

1. **Standard NDA Template**
   - URL: https://www.contractstandards.com/nda
   - Type: Non-Disclosure Agreement
   - Good for testing: confidentiality extraction, party identification

2. **Master Service Agreement (MSA)**
   - URL: https://www.contractstandards.com/msa
   - Type: Service Agreement
   - Good for testing: payment terms, termination, auto-renewal

3. **GitHub Terms of Service**
   - URL: https://github.com/github/site-policy/blob/master/github-terms-of-service.md
   - Type: ToS (convert PDF if needed)
   - Good for testing: liability caps, indemnification

4. **Mozilla Public License**
   - URL: https://opensource.org/licenses/MPL-2.0
   - Type: Open Source License
   - Good for testing: governing law, broad scope parsing

5. **Creative Commons License**
   - URL: https://creativecommons.org/licenses/by/4.0/legalcode
   - Type: License Agreement
   - Good for testing: structural complexity, multi-party terms

## Internal Documentation

- **README.md**: Main documentation and quick start guide
- **API_SPEC.md**: Complete API specification with examples
- **DEPLOYMENT.md**: Deployment guide for different environments
- **examples.py**: Python usage examples
- **client.py**: Python SDK implementation

## External Resources

### FastAPI
- Documentation: https://fastapi.tiangolo.com/
- Starlette: https://www.starlette.io/

### PDF Processing
- pdfplumber: https://github.com/jsvine/pdfplumber
- PyPDF: https://github.com/py-pdf/pypdf

### Vector Search
- ChromaDB: https://www.trychroma.com/
- Sentence Transformers: https://www.sbert.net/

### LLM Integration
- OpenAI API: https://platform.openai.com/
- Anthropic Claude: https://console.anthropic.com/
- Ollama (local): https://ollama.ai/

### Deployment
- Docker: https://www.docker.com/
- Kubernetes: https://kubernetes.io/
- AWS ECS: https://aws.amazon.com/ecs/
- Heroku: https://www.heroku.com/

### Monitoring
- Prometheus: https://prometheus.io/
- Grafana: https://grafana.com/
- ELK Stack: https://www.elastic.co/what-is/elk-stack

## Testing Resources

- pytest: https://docs.pytest.org/
- requests: https://requests.readthedocs.io/
- FastAPI TestClient: https://fastapi.tiangolo.com/advanced/testing-dependencies/

## Security Resources

- OWASP: https://owasp.org/
- JWT: https://jwt.io/
- OAuth 2.0: https://oauth.net/2/

---

## How to Download Sample PDFs

### Using curl
```bash
# Download GitHub ToS (if PDF available)
curl -o github-tos.pdf https://example.com/tos.pdf
```

### Convert to PDF
```bash
# If only HTML/Markdown available, use:
# - Online converters: https://cloudconvert.com/
# - Command line: wkhtmltopdf, pandoc
pandoc document.md -o document.pdf
```

### Create Sample PDFs
For testing, you can create simple PDFs with contract-like content:

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def create_sample_contract():
    c = canvas.Canvas("sample_contract.pdf", pagesize=letter)
    c.drawString(100, 750, "SAMPLE SERVICE AGREEMENT")
    c.drawString(100, 720, "This Agreement is entered into between Company A and Company B")
    c.drawString(100, 700, "Effective Date: January 1, 2025")
    c.drawString(100, 680, "Term: 12 months")
    c.drawString(100, 660, "Governing Law: New York")
    c.drawString(100, 640, "Payment Terms: Net 30")
    c.save()

create_sample_contract()
```

Then install: `pip install reportlab`
