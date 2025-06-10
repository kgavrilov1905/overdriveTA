from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging
from ..models.document import QueryRequest, QueryResponse
from ..services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest) -> QueryResponse:
    """Process a user query and return RAG-generated response"""
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Process the query through RAG pipeline
        result = await rag_service.process_query(
            query=request.query,
            max_results=request.max_results or 5
        )
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result.get("confidence")
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error while processing query")

@router.get("/status")
async def get_chat_status() -> Dict[str, Any]:
    """Get status of the RAG system components"""
    try:
        status = rag_service.get_system_status()
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving system status")

@router.get("/documents")
async def get_available_documents() -> Dict[str, Any]:
    """Get list of available documents in the system"""
    try:
        documents = await rag_service.get_available_documents()
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error getting available documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving documents") 