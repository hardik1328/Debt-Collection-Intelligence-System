"""
Client library for Contract Intelligence API
"""
import requests
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class ContractIntelligenceAPI:
    """Python client for Contract Intelligence API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
    
    # Ingestion
    def ingest(self, file_paths: List[str]) -> Tuple[List[str], List[Dict]]:
        """Upload PDF documents"""
        files = []
        try:
            for path in file_paths:
                file_path = Path(path)
                if not file_path.exists():
                    raise FileNotFoundError(f"File not found: {path}")
                files.append(("files", open(file_path, "rb")))
            
            response = self.session.post(f"{self.base_url}/ingest", files=files)
            response.raise_for_status()
            data = response.json()
            return data["document_ids"], data["documents"]
        finally:
            for _, file_obj in files:
                file_obj.close()
    
    def list_documents(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        """List ingested documents"""
        response = self.session.get(
            f"{self.base_url}/ingest/documents",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_document(self, document_id: str) -> Dict:
        """Get document details"""
        response = self.session.get(f"{self.base_url}/ingest/documents/{document_id}")
        response.raise_for_status()
        return response.json()
    
    def delete_document(self, document_id: str) -> Dict:
        """Delete a document"""
        response = self.session.delete(f"{self.base_url}/ingest/documents/{document_id}")
        response.raise_for_status()
        return response.json()
    
    # Extraction
    def extract_fields(self, document_id: str) -> Dict:
        """Extract structured fields from contract"""
        response = self.session.post(
            f"{self.base_url}/extract",
            params={"document_id": document_id}
        )
        response.raise_for_status()
        return response.json()
    
    def get_extracted_fields(self, document_id: str) -> Dict:
        """Get previously extracted fields"""
        response = self.session.get(f"{self.base_url}/extract/fields/{document_id}")
        response.raise_for_status()
        return response.json()
    
    # Question Answering
    def ask(self, question: str, document_ids: Optional[List[str]] = None, top_k: int = 5) -> Dict:
        """Ask a question about contracts"""
        response = self.session.post(
            f"{self.base_url}/ask",
            json={
                "question": question,
                "document_ids": document_ids,
                "top_k": top_k
            }
        )
        response.raise_for_status()
        return response.json()
    
    def stream_answer(self, question: str, document_ids: Optional[str] = None, top_k: int = 5):
        """Stream answer tokens"""
        params = {
            "question": question,
            "top_k": top_k
        }
        if document_ids:
            params["document_ids"] = ",".join(document_ids) if isinstance(document_ids, list) else document_ids
        
        response = self.session.get(
            f"{self.base_url}/ask/stream",
            params=params,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                data = line.decode("utf-8")
                if data.startswith("data: "):
                    chunk = data[6:]
                    if chunk != "[DONE]":
                        try:
                            yield json.loads(chunk)
                        except json.JSONDecodeError:
                            yield {"error": chunk}
    
    def get_query_history(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        """Get query history"""
        response = self.session.get(
            f"{self.base_url}/ask/queries",
            params={"skip": skip, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    # Audit
    def audit(self, document_id: str) -> Dict:
        """Run risk audit on contract"""
        response = self.session.post(
            f"{self.base_url}/audit",
            params={"document_id": document_id}
        )
        response.raise_for_status()
        return response.json()
    
    def get_audit_findings(self, document_id: str, severity: Optional[str] = None) -> List[Dict]:
        """Get audit findings for document"""
        params = {}
        if severity:
            params["severity"] = severity
        
        response = self.session.get(
            f"{self.base_url}/audit/findings/{document_id}",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_audit_summary(self, document_id: str) -> Dict:
        """Get audit summary for document"""
        response = self.session.get(f"{self.base_url}/audit/summary/{document_id}")
        response.raise_for_status()
        return response.json()
    
    # Admin
    def health_check(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/admin/healthz")
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict:
        """Get system metrics"""
        response = self.session.get(f"{self.base_url}/admin/metrics")
        response.raise_for_status()
        return response.json()
    
    def get_status(self) -> Dict:
        """Get detailed system status"""
        response = self.session.get(f"{self.base_url}/admin/status")
        response.raise_for_status()
        return response.json()
    
    # Webhooks
    def register_webhook(self, url: str, events: List[str]) -> Dict:
        """Register webhook"""
        response = self.session.post(
            f"{self.base_url}/webhooks/register",
            json={"url": url, "events": events}
        )
        response.raise_for_status()
        return response.json()
    
    def list_webhooks(self) -> List[Dict]:
        """List registered webhooks"""
        response = self.session.get(f"{self.base_url}/webhooks/list")
        response.raise_for_status()
        return response.json()
    
    def unregister_webhook(self, webhook_id: str) -> Dict:
        """Unregister webhook"""
        response = self.session.delete(f"{self.base_url}/webhooks/{webhook_id}")
        response.raise_for_status()
        return response.json()


# Usage examples
if __name__ == "__main__":
    client = ContractIntelligenceAPI("http://localhost:8000")
    
    # Check health
    print("Health:", client.health_check())
    
    # Upload contracts
    # doc_ids, docs = client.ingest(["contract1.pdf", "contract2.pdf"])
    # print(f"Uploaded {len(doc_ids)} documents")
    
    # Extract fields
    # fields = client.extract_fields(doc_ids[0])
    # print(f"Parties: {fields['parties']}")
    
    # Ask question
    # answer = client.ask("What is the payment term?", doc_ids)
    # print(f"Answer: {answer['answer']}")
    
    # Run audit
    # audit = client.audit(doc_ids[0])
    # print(f"Findings: {len(audit['findings'])}")
    
    # Get metrics
    metrics = client.get_metrics()
    print("Metrics:", metrics)
