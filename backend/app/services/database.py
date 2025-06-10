import os
from typing import List, Optional, Dict, Any
from supabase import create_client, Client
from datetime import datetime
import json

class DatabaseService:
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL")
        # Try multiple possible environment variable names
        supabase_key = (os.getenv("SUPABASE_ANON_KEY") or 
                       os.getenv("SUPABASE_PUBLIC") or 
                       os.getenv("SUPABASE_KEY"))
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase credentials not found in environment variables. Please set SUPABASE_URL and SUPABASE_ANON_KEY (or SUPABASE_PUBLIC)")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    # Document operations
    async def create_document(self, title: str, filename: str, file_size: int, content_type: str) -> Dict[str, Any]:
        """Create a new document record"""
        data = {
            "title": title,
            "filename": filename,
            "file_size": file_size,
            "content_type": content_type,
            "upload_date": datetime.now().isoformat(),
            "processed": False
        }
        
        result = self.supabase.table("documents").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        result = self.supabase.table("documents").select("*").eq("id", document_id).execute()
        return result.data[0] if result.data else None
    
    async def update_document_processed(self, document_id: int, processed: bool = True):
        """Mark a document as processed"""
        result = self.supabase.table("documents").update({"processed": processed}).eq("id", document_id).execute()
        return result.data[0] if result.data else None
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents"""
        result = self.supabase.table("documents").select("*").order("upload_date", desc=True).execute()
        return result.data or []
    
    # Document chunk operations
    async def create_document_chunk(self, document_id: int, chunk_text: str, chunk_index: int, 
                                  page_number: Optional[int] = None, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Create a new document chunk"""
        data = {
            "document_id": document_id,
            "chunk_text": chunk_text,
            "chunk_index": chunk_index,
            "page_number": page_number,
            "metadata": metadata,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("document_chunks").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_chunks_by_document(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all chunks for a document"""
        result = self.supabase.table("document_chunks").select("*").eq("document_id", document_id).order("chunk_index").execute()
        return result.data or []
    
    # Embedding operations
    async def create_embedding(self, chunk_id: int, embedding_vector: List[float], model_name: str) -> Dict[str, Any]:
        """Create an embedding for a chunk"""
        data = {
            "chunk_id": chunk_id,
            "embedding_vector": embedding_vector,
            "model_name": model_name,
            "created_at": datetime.now().isoformat()
        }
        
        result = self.supabase.table("embeddings").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def similarity_search(self, query_embedding: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search using vector embeddings"""
        # Using Supabase's vector similarity search
        # This requires pgvector extension to be enabled in Supabase
        rpc_result = self.supabase.rpc(
            "similarity_search",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.3,  # Lower threshold for better recall
                "match_count": limit
            }
        ).execute()
        
        return rpc_result.data or []
    
    async def get_chunk_with_document(self, chunk_id: int) -> Optional[Dict[str, Any]]:
        """Get chunk with associated document information"""
        result = self.supabase.table("document_chunks").select(
            "*, documents(*)"
        ).eq("id", chunk_id).execute()
        
        return result.data[0] if result.data else None

# Singleton instance
db_service = DatabaseService() 