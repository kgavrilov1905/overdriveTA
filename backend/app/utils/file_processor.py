import os
import asyncio
from typing import Dict, Any, List
import logging
from ..services.database import db_service
from ..services.document_processor import document_processor
from ..services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self):
        pass
    
    async def process_uploaded_file(self, file_content: bytes, filename: str, content_type: str) -> Dict[str, Any]:
        """Process an uploaded file through the complete pipeline"""
        try:
            logger.info(f"Starting processing of file: {filename}")
            
            # Step 1: Create document record
            file_size = len(file_content)
            
            # Extract title from document content
            full_text, pages_data = await document_processor.extract_text_from_pdf(file_content)
            title = await document_processor.get_document_title(full_text, filename)
            
            # Create document in database
            document = await db_service.create_document(title, filename, file_size, content_type)
            if not document:
                raise Exception("Failed to create document record")
            
            document_id = document["id"]
            logger.info(f"Created document record with ID: {document_id}")
            
            # Step 2: Create intelligent chunks
            chunks = await document_processor.create_intelligent_chunks(full_text, pages_data)
            logger.info(f"Created {len(chunks)} chunks for document")
            
            # Step 3: Store chunks in database
            chunk_records = []
            for chunk_data in chunks:
                chunk_record = await db_service.create_document_chunk(
                    document_id=document_id,
                    chunk_text=chunk_data["chunk_text"],
                    chunk_index=chunk_data["chunk_index"],
                    page_number=chunk_data.get("page_number"),
                    metadata=chunk_data.get("metadata")
                )
                if chunk_record:
                    chunk_records.append(chunk_record)
            
            logger.info(f"Stored {len(chunk_records)} chunks in database")
            
            # Step 4: Generate embeddings for chunks
            embeddings_created = 0
            embedding_model_info = embedding_service.get_model_info()
            
            # Process embeddings in batches to avoid overwhelming the API
            batch_size = 10
            for i in range(0, len(chunk_records), batch_size):
                batch_chunks = chunk_records[i:i + batch_size]
                batch_texts = [chunk["chunk_text"] for chunk in batch_chunks]
                
                try:
                    # Generate batch embeddings
                    batch_embeddings = await embedding_service.generate_batch_embeddings(batch_texts)
                    
                    # Store embeddings in database
                    for chunk, embedding in zip(batch_chunks, batch_embeddings):
                        embedding_record = await db_service.create_embedding(
                            chunk_id=chunk["id"],
                            embedding_vector=embedding,
                            model_name=embedding_model_info["model_name"]
                        )
                        if embedding_record:
                            embeddings_created += 1
                    
                    logger.info(f"Processed batch {i//batch_size + 1}, embeddings created: {embeddings_created}")
                    
                    # Small delay to be respectful to APIs
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error processing embedding batch {i//batch_size + 1}: {str(e)}")
                    continue
            
            # Step 5: Mark document as processed
            await db_service.update_document_processed(document_id, True)
            
            logger.info(f"Successfully processed document {filename}: {len(chunk_records)} chunks, {embeddings_created} embeddings")
            
            return {
                "success": True,
                "document_id": document_id,
                "title": title,
                "chunks_created": len(chunk_records),
                "embeddings_created": embeddings_created,
                "pages_processed": len(pages_data)
            }
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "filename": filename
            }
    
    async def process_sample_documents(self, samples_dir: str = "samples") -> List[Dict[str, Any]]:
        """Process all PDF documents in the samples directory"""
        results = []
        
        if not os.path.exists(samples_dir):
            logger.error(f"Samples directory not found: {samples_dir}")
            return results
        
        # Get all PDF files from samples directory
        pdf_files = [f for f in os.listdir(samples_dir) if f.lower().endswith('.pdf')]
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for filename in pdf_files:
            try:
                file_path = os.path.join(samples_dir, filename)
                
                # Read file content
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Process the file
                result = await self.process_uploaded_file(
                    file_content=file_content,
                    filename=filename,
                    content_type="application/pdf"
                )
                
                results.append(result)
                logger.info(f"Processed {filename}: {'Success' if result['success'] else 'Failed'}")
                
            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                results.append({
                    "success": False,
                    "error": str(e),
                    "filename": filename
                })
        
        return results
    
    async def get_processing_status(self) -> Dict[str, Any]:
        """Get status of document processing"""
        try:
            documents = await db_service.list_documents()
            
            total_docs = len(documents)
            processed_docs = len([doc for doc in documents if doc.get('processed', False)])
            
            return {
                "total_documents": total_docs,
                "processed_documents": processed_docs,
                "pending_documents": total_docs - processed_docs,
                "documents": documents
            }
            
        except Exception as e:
            logger.error(f"Error getting processing status: {str(e)}")
            return {
                "total_documents": 0,
                "processed_documents": 0,
                "pending_documents": 0,
                "error": str(e)
            }

# Singleton instance
file_processor = FileProcessor() 