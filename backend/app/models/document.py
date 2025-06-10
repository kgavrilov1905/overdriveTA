from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class DocumentBase(BaseModel):
    title: str
    filename: str
    file_size: int
    content_type: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    upload_date: datetime
    processed: bool = False
    
    class Config:
        from_attributes = True

class DocumentChunkBase(BaseModel):
    document_id: int
    chunk_text: str
    chunk_index: int
    page_number: Optional[int] = None
    metadata: Optional[dict] = None

class DocumentChunkCreate(DocumentChunkBase):
    pass

class DocumentChunk(DocumentChunkBase):
    id: int
    embedding_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class EmbeddingBase(BaseModel):
    chunk_id: int
    embedding_vector: List[float]
    model_name: str

class EmbeddingCreate(EmbeddingBase):
    pass

class Embedding(EmbeddingBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: Optional[float] = None 