from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
import logging
import uuid
import json
import time
import asyncio
from typing import Optional, List

from app.models.schemas import AskRequest, AskResponse, CitationSpan
from app.models.database import Contract, QueryLog, get_session_local
from app.services.llm_service import get_llm_provider
from app.services.embedding_service import VectorStore, EmbeddingService
from app.core.config import get_settings
from app.core.logger import logger

router = APIRouter(prefix="/ask", tags=["ask"])

# Global services
vector_store = None
embedding_service = None


def get_services():
    """Initialize services"""
    global vector_store, embedding_service
    if vector_store is None:
        settings = get_settings()
        vector_store = VectorStore(
            use_chromadb=settings.vector_store_type == "chromadb",
            persist_dir=settings.chromadb_dir
        )
        embedding_service = EmbeddingService(settings.embedding_model)
    return vector_store, embedding_service


def get_db():
    """Get database session"""
    settings = get_settings()
    SessionLocal = get_session_local(settings.database_url)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=AskResponse)
async def ask_question(
    request: AskRequest,
    db=Depends(get_db)
):
    """
    Ask a question about contract(s)
    
    - **question**: The question to ask
    - **document_ids**: Optional list of specific documents to search
    - **top_k**: Number of relevant passages to retrieve (default: 5)
    - Returns: Answer with citations to source documents
    """
    settings = get_settings()
    
    try:
        vs, es = get_services()
        
        # Get document IDs
        doc_ids = request.document_ids
        if not doc_ids:
            # Get all documents if none specified
            contracts = db.query(Contract).all()
            doc_ids = [c.id for c in contracts]
        
        if not doc_ids:
            raise HTTPException(status_code=400, detail="No documents available")
        
        # Ensure documents are in vector store
        for doc_id in doc_ids:
            contract = db.query(Contract).filter(Contract.id == doc_id).first()
            if contract and contract.raw_text:
                vs.add_document(doc_id, contract.raw_text, {"filename": contract.filename})
        
        # Search vector store
        search_results = vs.search(request.question, top_k=request.top_k, doc_ids=doc_ids)
        
        if not search_results:
            return AskResponse(
                question=request.question,
                answer="No relevant information found in documents.",
                citations=[]
            )
        
        # Prepare context from search results
        context_parts = []
        citations = []
        for doc_id, text, score in search_results:
            context_parts.append(f"[Document {doc_id}]:\n{text}")
            
            # Create citation (simplified - ideally we'd track exact positions)
            citations.append(CitationSpan(
                document_id=doc_id,
                page=1,  # Ideally tracked during embedding
                start_char=0,
                end_char=min(len(text), 200),
                text=text[:200]
            ))
        
        context = "\n\n".join(context_parts)
        
        # Get LLM provider and answer question
        llm_provider = get_llm_provider(
            settings.llm_provider,
            settings.openai_api_key or settings.anthropic_api_key,
            settings.model_name
        )
        
        start_time = time.time()
        answer = await llm_provider.answer_question(request.question, context)
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Log query
        query_log = QueryLog(
            id=str(uuid.uuid4()),
            question=request.question,
            answer=answer,
            document_ids=json.dumps(doc_ids),
            query_time_ms=query_time
        )
        db.add(query_log)
        db.commit()
        
        logger.info(f"Answered question in {query_time:.2f}ms")
        
        return AskResponse(
            question=request.question,
            answer=answer,
            citations=citations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question answering failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")


@router.get("/stream")
async def ask_stream(
    question: str = Query(...),
    document_ids: Optional[str] = Query(None),  # Comma-separated
    top_k: int = Query(5),
    db=Depends(get_db)
):
    """
    Stream tokens while answering a question (Server-Sent Events)
    
    - **question**: The question to ask
    - **document_ids**: Optional comma-separated document IDs
    - **top_k**: Number of relevant passages to retrieve
    """
    settings = get_settings()
    
    async def generate():
        try:
            vs, es = get_services()
            
            # Parse document IDs
            doc_ids = None
            if document_ids:
                doc_ids = [d.strip() for d in document_ids.split(",")]
            else:
                contracts = db.query(Contract).all()
                doc_ids = [c.id for c in contracts]
            
            if not doc_ids:
                yield f"data: {json.dumps({'error': 'No documents available'})}\n\n"
                return
            
            # Ensure documents are in vector store
            for doc_id in doc_ids:
                contract = db.query(Contract).filter(Contract.id == doc_id).first()
                if contract and contract.raw_text:
                    vs.add_document(doc_id, contract.raw_text, {"filename": contract.filename})
            
            # Search vector store
            search_results = vs.search(question, top_k=top_k, doc_ids=doc_ids)
            
            if not search_results:
                yield f"data: {json.dumps({'chunk': 'No relevant information found in documents.'})}\n\n"
                yield "data: [DONE]\n\n"
                return
            
            # Prepare context
            context_parts = []
            for doc_id, text, score in search_results:
                context_parts.append(f"[Document {doc_id}]:\n{text}")
            
            context = "\n\n".join(context_parts)
            
            # Get LLM provider
            llm_provider = get_llm_provider(
                settings.llm_provider,
                settings.openai_api_key or settings.anthropic_api_key,
                settings.model_name
            )
            
            # Stream answer tokens (simulated with OpenAI streaming if available)
            try:
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=settings.openai_api_key)
                
                stream = await client.chat.completions.create(
                    model=settings.model_name,
                    messages=[
                        {"role": "system", "content": "You are a contract analysis expert. Answer based on provided context."},
                        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
                    ],
                    temperature=0.2,
                    max_tokens=1000,
                    stream=True
                )
                
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        yield f"data: {json.dumps({'chunk': token})}\n\n"
                        await asyncio.sleep(0.01)  # Simulate streaming delay
                
            except Exception:
                # Fallback: non-streaming response split into chunks
                answer = await llm_provider.answer_question(question, context)
                for chunk in answer.split():
                    yield f"data: {json.dumps({'chunk': chunk + ' '})}\n\n"
                    await asyncio.sleep(0.01)
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"Streaming failed: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/queries", tags=["ask"])
async def get_query_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db=Depends(get_db)
):
    """Get query history"""
    try:
        queries = db.query(QueryLog).offset(skip).limit(limit).all()
        return [
            {
                "id": q.id,
                "question": q.question,
                "answer": q.answer[:500] if q.answer else None,
                "document_ids": json.loads(q.document_ids) if q.document_ids else [],
                "query_time_ms": q.query_time_ms,
                "query_date": q.query_date.isoformat()
            }
            for q in queries
        ]
    except Exception as e:
        logger.error(f"Failed to get query history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve query history")
