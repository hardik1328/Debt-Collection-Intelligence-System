"""
Test suite for Contract Intelligence API
"""
import pytest
import asyncio
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import app
from app.models.database import create_tables, get_session_local
from app.core.config import get_settings

# Initialize test client
client = TestClient(app)


class TestIngest:
    """Test ingestion endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/admin/healthz")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_list_documents_empty(self):
        """Test listing documents when empty"""
        response = client.get("/ingest/documents")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_metrics(self):
        """Test metrics endpoint"""
        response = client.get("/admin/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "documents_ingested" in data
        assert "total_queries" in data


class TestExtraction:
    """Test extraction endpoints"""
    
    def test_extract_fields_not_found(self):
        """Test extraction with non-existent document"""
        response = client.post("/extract?document_id=nonexistent")
        assert response.status_code == 404


class TestAsk:
    """Test Q&A endpoints"""
    
    def test_ask_no_documents(self):
        """Test asking question with no documents"""
        response = client.post("/ask", json={
            "question": "What is the payment term?",
            "document_ids": []
        })
        # Should fail because no documents
        assert response.status_code in [400, 500]


class TestAudit:
    """Test audit endpoints"""
    
    def test_audit_not_found(self):
        """Test audit with non-existent document"""
        response = client.post("/audit?document_id=nonexistent")
        assert response.status_code == 404


class TestAdmin:
    """Test admin endpoints"""
    
    def test_status_endpoint(self):
        """Test status endpoint"""
        response = client.get("/admin/status")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "system" in data


@pytest.mark.asyncio
async def test_pdf_service():
    """Test PDF extraction service"""
    from app.services.pdf_service import PDFExtractor
    
    # Create a dummy PDF for testing (in real test, would use fixture)
    # This test is placeholder
    pass


@pytest.mark.asyncio
async def test_llm_service():
    """Test LLM service"""
    from app.services.llm_service import get_llm_provider, LocalLLMProvider
    
    provider = get_llm_provider("local")
    assert isinstance(provider, LocalLLMProvider)
    
    # Test extraction
    sample_text = "Agreement between Company A and Company B, effective 2025-01-01"
    fields = await provider.extract_fields(sample_text)
    assert isinstance(fields, dict)


@pytest.mark.asyncio
async def test_embedding_service():
    """Test embedding service"""
    from app.services.embedding_service import EmbeddingService
    
    service = EmbeddingService()
    embedding = service.embed_text("sample contract text")
    assert embedding is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
