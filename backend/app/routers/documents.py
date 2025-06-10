from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any, List
import logging
from ..utils.file_processor import file_processor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and process a PDF document"""
    try:
        # Validate file type
        if not file.content_type == "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must have .pdf extension")
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Process the file
        result = await file_processor.process_uploaded_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Failed to process document: {result.get('error', 'Unknown error')}")
        
        return {
            "message": "Document uploaded and processed successfully",
            "document_id": result["document_id"],
            "title": result["title"],
            "chunks_created": result["chunks_created"],
            "embeddings_created": result["embeddings_created"],
            "pages_processed": result["pages_processed"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during file upload")

@router.post("/process-samples")
async def process_sample_documents() -> Dict[str, Any]:
    """Process all PDF documents in the samples directory"""
    try:
        results = await file_processor.process_sample_documents()
        
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]
        
        return {
            "message": f"Processed {len(results)} documents",
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error processing sample documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing sample documents")

@router.get("/status")
async def get_processing_status() -> Dict[str, Any]:
    """Get document processing status"""
    try:
        status = await file_processor.get_processing_status()
        return status
    except Exception as e:
        logger.error(f"Error getting processing status: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving processing status")

@router.get("/")
async def list_documents() -> Dict[str, Any]:
    """List all documents in the system"""
    try:
        status = await file_processor.get_processing_status()
        return {
            "documents": status.get("documents", []),
            "total": status.get("total_documents", 0),
            "processed": status.get("processed_documents", 0),
            "pending": status.get("pending_documents", 0)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving documents") 