"""
Example usage and integration patterns
"""

# Example 1: Upload and Extract
example_ingest_and_extract = """
import requests

BASE_URL = "http://localhost:8000"

# 1. Upload PDF
with open("contract.pdf", "rb") as f:
    response = requests.post(
        f"{BASE_URL}/ingest",
        files={"files": f}
    )
    doc_id = response.json()["document_ids"][0]

# 2. Extract fields
response = requests.post(f"{BASE_URL}/extract?document_id={doc_id}")
fields = response.json()
print(f"Parties: {fields['parties']}")
print(f"Governing Law: {fields['governing_law']}")
print(f"Liability Cap: {fields['liability_cap']}")
"""

# Example 2: Ask Questions
example_ask_questions = """
import requests

BASE_URL = "http://localhost:8000"

# Ask multiple questions about contract
questions = [
    "What is the payment term?",
    "Who are the parties to this agreement?",
    "What is the governing law?",
    "What are the termination conditions?"
]

for question in questions:
    response = requests.post(
        f"{BASE_URL}/ask",
        json={
            "question": question,
            "document_ids": ["DOC_ID"],
            "top_k": 5
        }
    )
    answer = response.json()
    print(f"Q: {question}")
    print(f"A: {answer['answer']}")
    print(f"Citations: {answer['citations']}")
    print()
"""

# Example 3: Risk Audit
example_risk_audit = """
import requests

BASE_URL = "http://localhost:8000"

# Run audit
response = requests.post(f"{BASE_URL}/audit?document_id=DOC_ID")
audit = response.json()

print(f"Summary: {audit['summary']}")
for finding in audit['findings']:
    print(f"- {finding['clause_type']} ({finding['severity']}): {finding['description']}")
    if finding['recommendation']:
        print(f"  Recommendation: {finding['recommendation']}")
"""

# Example 4: Streaming
example_streaming = """
import requests

BASE_URL = "http://localhost:8000"

# Stream answer tokens
response = requests.get(
    f"{BASE_URL}/ask/stream",
    params={
        "question": "What are the key terms?",
        "top_k": 5
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        data = line.decode("utf-8")
        if data.startswith("data: "):
            chunk = data[6:]
            if chunk != "[DONE]":
                print(chunk, end="", flush=True)
"""

# Example 5: Webhooks
example_webhooks = """
import requests
from flask import Flask, request

BASE_URL = "http://localhost:8000"
app = Flask(__name__)

# 1. Register webhook
response = requests.post(
    f"{BASE_URL}/webhooks/register",
    json={
        "url": "https://your-domain.com/webhook",
        "events": ["extraction_complete", "audit_complete"]
    }
)
webhook_id = response.json()["webhook_id"]

# 2. Receive webhook events
@app.route("/webhook", methods=["POST"])
def receive_webhook():
    event = request.json
    print(f"Event: {event['event_type']}")
    print(f"Task: {event['task_id']}")
    print(f"Data: {event['data']}")
    return {"status": "received"}

# 3. Run extraction (will trigger webhook)
# curl -X POST http://localhost:8000/extract?document_id=DOC_ID
"""

# Example 6: Batch Processing
example_batch_processing = """
import requests
import glob

BASE_URL = "http://localhost:8000"

# 1. Upload all PDFs in a directory
pdf_files = glob.glob("contracts/*.pdf")
doc_ids = []

for pdf_file in pdf_files:
    with open(pdf_file, "rb") as f:
        response = requests.post(
            f"{BASE_URL}/ingest",
            files={"files": f}
        )
        doc_ids.extend(response.json()["document_ids"])

# 2. Extract fields from all
results = {}
for doc_id in doc_ids:
    response = requests.post(f"{BASE_URL}/extract?document_id={doc_id}")
    results[doc_id] = response.json()

# 3. Run audits on all
audits = {}
for doc_id in doc_ids:
    response = requests.post(f"{BASE_URL}/audit?document_id={doc_id}")
    audits[doc_id] = response.json()

# 4. Generate report
print(f"Processed {len(doc_ids)} contracts")
for doc_id, audit in audits.items():
    print(f"{doc_id}: {audit['summary']}")
"""

# Example 7: Python SDK (if wrapped)
example_sdk = """
from contract_intelligence import ContractAPI

api = ContractAPI("http://localhost:8000")

# Upload
doc_id = api.ingest("contract.pdf")[0]

# Extract
fields = api.extract(doc_id)

# Ask
answer = api.ask("What is the liability cap?", doc_id)

# Audit
findings = api.audit(doc_id)
"""

if __name__ == "__main__":
    print("# Example 1: Ingest and Extract")
    print(example_ingest_and_extract)
    print("\n# Example 2: Ask Questions")
    print(example_ask_questions)
    print("\n# Example 3: Risk Audit")
    print(example_risk_audit)
    print("\n# Example 4: Streaming")
    print(example_streaming)
    print("\n# Example 5: Webhooks")
    print(example_webhooks)
    print("\n# Example 6: Batch Processing")
    print(example_batch_processing)
    print("\n# Example 7: Python SDK")
    print(example_sdk)
