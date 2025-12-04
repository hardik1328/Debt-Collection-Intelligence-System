import logging
from typing import List, Dict, Tuple, Optional
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding and vector search service"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            logger.info(f"Loaded embedding model: {model_name}")
        except ImportError:
            logger.error("sentence-transformers not available")
            self.model = None
    
    def embed_text(self, text: str) -> np.ndarray:
        """Embed text to vector"""
        if not self.model:
            return np.zeros(384)
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            return np.zeros(384)
    
    def embed_documents(self, texts: List[str]) -> List[np.ndarray]:
        """Embed multiple documents"""
        if not self.model:
            return [np.zeros(384) for _ in texts]
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [embeddings[i] for i in range(len(texts))]
        except Exception as e:
            logger.error(f"Batch embedding failed: {str(e)}")
            return [np.zeros(384) for _ in texts]
    
    def similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between vectors"""
        if vec1.size == 0 or vec2.size == 0:
            return 0.0
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


class VectorStore:
    """Vector storage and retrieval"""
    
    def __init__(self, use_chromadb: bool = True, persist_dir: str = "./data/chroma"):
        self.use_chromadb = use_chromadb
        self.persist_dir = persist_dir
        self.documents_store = {}  # In-memory fallback
        self.embeddings_store = {}
        
        if use_chromadb:
            try:
                import chromadb
                self.client = chromadb.PersistentClient(path=persist_dir)
                self.collection = self.client.get_or_create_collection(
                    name="contracts",
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info("ChromaDB initialized")
            except Exception as e:
                logger.warning(f"ChromaDB init failed, using in-memory store: {str(e)}")
                self.use_chromadb = False
    
    def add_document(self, doc_id: str, text: str, metadata: Dict = None):
        """Add document to vector store"""
        if not metadata:
            metadata = {}
        
        try:
            if self.use_chromadb and hasattr(self, 'collection'):
                self.collection.add(
                    ids=[doc_id],
                    documents=[text],
                    metadatas=[metadata]
                )
            else:
                self.documents_store[doc_id] = {
                    "text": text,
                    "metadata": metadata
                }
            logger.info(f"Added document {doc_id} to vector store")
        except Exception as e:
            logger.error(f"Failed to add document: {str(e)}")
    
    def search(self, query: str, top_k: int = 5, doc_ids: List[str] = None) -> List[Tuple[str, str, float]]:
        """Search vector store"""
        try:
            if self.use_chromadb and hasattr(self, 'collection'):
                where_clause = None
                if doc_ids:
                    where_clause = {"$or": [{"document_id": doc_id} for doc_id in doc_ids]}
                
                results = self.collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where_clause if doc_ids else None
                )
                
                # Format results
                formatted_results = []
                if results and results['ids'] and len(results['ids']) > 0:
                    for i, doc_id in enumerate(results['ids'][0]):
                        score = results['distances'][0][i] if results['distances'] else 0
                        text = results['documents'][0][i] if results['documents'] else ""
                        # ChromaDB returns distances, convert to similarity
                        similarity = 1 - (score / 2) if score else 0
                        formatted_results.append((doc_id, text, similarity))
                
                return formatted_results
            else:
                return self._search_in_memory(query, top_k, doc_ids)
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []
    
    def _search_in_memory(self, query: str, top_k: int = 5, doc_ids: List[str] = None) -> List[Tuple[str, str, float]]:
        """Simple in-memory search using keyword matching"""
        query_lower = query.lower()
        results = []
        
        for doc_id, doc_data in self.documents_store.items():
            if doc_ids and doc_id not in doc_ids:
                continue
            
            text = doc_data["text"]
            # Simple keyword matching score
            score = sum(1 for word in query_lower.split() if word in text.lower())
            
            if score > 0:
                results.append((doc_id, text, score / len(query_lower.split())))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:top_k]
    
    def delete_document(self, doc_id: str):
        """Delete document from vector store"""
        try:
            if self.use_chromadb and hasattr(self, 'collection'):
                self.collection.delete(ids=[doc_id])
            else:
                self.documents_store.pop(doc_id, None)
            logger.info(f"Deleted document {doc_id}")
        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
