import os
import openai
from typing import List, Dict, Any, Optional
import logging
import asyncio
from .database import db_service
from .embedding_service import embedding_service

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.gemini_client = None
        self.openai_client = None
        
        # Try to initialize Gemini first (free!)
        if GEMINI_AVAILABLE and self._initialize_gemini():
            self.llm_model = "gemini-2.0-flash-exp"
            logger.info("Using Gemini 2.0 Flash (free)")
        elif self._initialize_openai():
            self.llm_model = "gpt-4o-mini"
            logger.info("Using OpenAI GPT models")
        else:
            logger.warning("No LLM API key found. LLM functionality will be limited.")
    
    def _initialize_gemini(self) -> bool:
        """Initialize Google Gemini API for LLM"""
        try:
            # Try both GOOGLE_API_KEY and GEMINI_API_KEY for flexibility
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                return False
            
            # Initialize the Gemini API
            genai.configure(api_key=api_key)
            self.gemini_client = True
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini for LLM: {str(e)}")
            return False
    
    def _initialize_openai(self) -> bool:
        """Initialize OpenAI client as fallback"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                return True
            return False
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI: {str(e)}")
            return False
    
    async def process_query(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Main RAG pipeline: process query and return answer with sources"""
        try:
            # Step 1: Generate query embedding
            query_embedding = await embedding_service.generate_query_embedding(query)
            
            # Step 2: Retrieve relevant context
            relevant_chunks = await self._retrieve_relevant_chunks(query_embedding, max_results)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find any relevant information to answer your question. This might be because the documents haven't been processed yet or your query doesn't match the available content.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Step 3: Format context for LLM
            context = await self._format_context(relevant_chunks)
            
            # Step 4: Generate answer using LLM
            answer = await self._generate_answer(query, context)
            
            # Step 5: Format sources
            sources = await self._format_sources(relevant_chunks)
            
            # Step 6: Calculate confidence score
            confidence = self._calculate_confidence(relevant_chunks, answer)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "I encountered an error while processing your question. Please try again or rephrase your question.",
                "sources": [],
                "confidence": 0.0
            }
    
    async def _retrieve_relevant_chunks(self, query_embedding: List[float], max_results: int) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks using vector similarity"""
        try:
            # Use database service to perform similarity search
            search_results = await db_service.similarity_search(query_embedding, max_results)
            
            # Enrich results with document information
            enriched_results = []
            for result in search_results:
                # Get chunk with document info
                chunk_with_doc = await db_service.get_chunk_with_document(result.get('chunk_id'))
                
                if chunk_with_doc:
                    enriched_results.append({
                        **chunk_with_doc,
                        'similarity_score': result.get('similarity', 0.0)
                    })
            
            return enriched_results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant chunks: {str(e)}")
            return []
    
    async def _format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context for the LLM"""
        if not chunks:
            return ""
        
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            document = chunk.get('documents', {})
            doc_title = document.get('title', 'Unknown Document')
            page_num = chunk.get('page_number', 'Unknown')
            chunk_text = chunk.get('chunk_text', '')
            
            context_part = f"""
[Source {i}: {doc_title}, Page {page_num}]
{chunk_text}
"""
            context_parts.append(context_part.strip())
        
        return "\n\n".join(context_parts)
    
    async def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer using LLM with the provided context"""
        if self.gemini_client:
            return await self._generate_gemini_answer(query, context)
        elif self.openai_client:
            return await self._generate_openai_answer(query, context)
        else:
            return self._generate_fallback_answer(context)
    
    async def _generate_gemini_answer(self, query: str, context: str) -> str:
        """Generate answer using Gemini 2.0 Flash"""
        try:
            # Create a comprehensive prompt for economic research queries
            system_instruction = """You are an expert AI assistant specializing in economic research and business insights for Alberta, Canada. You help users understand economic data, trends, and business conditions based on research reports.

Your responses should be:
- Accurate and based solely on the provided context
- Well-structured and easy to understand
- Professional but accessible
- Focused on actionable insights when possible
- Clear about limitations if information is incomplete

If the context doesn't contain enough information to answer the question, say so clearly."""

            user_prompt = f"""Context from economic research documents:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If specific data or statistics are mentioned, include them in your response. If the context doesn't fully address the question, clearly state what information is missing."""

            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _generate_sync():
                model = genai.GenerativeModel(
                    model_name=self.llm_model,
                    system_instruction=system_instruction
                )
                
                response = model.generate_content(
                    user_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,  # Lower temperature for more factual responses
                        max_output_tokens=1000,
                        top_p=0.8,
                        top_k=40
                    )
                )
                return response.text
            
            answer = await loop.run_in_executor(None, _generate_sync)
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Error generating Gemini answer: {str(e)}")
            # Fallback to OpenAI if available
            if self.openai_client:
                return await self._generate_openai_answer(query, context)
            return self._generate_fallback_answer(context)
    
    async def _generate_openai_answer(self, query: str, context: str) -> str:
        """Generate answer using OpenAI GPT (fallback)"""
        try:
            # Create a comprehensive prompt for economic research queries
            system_prompt = """You are an expert AI assistant specializing in economic research and business insights for Alberta, Canada. You help users understand economic data, trends, and business conditions based on research reports.

Your responses should be:
- Accurate and based solely on the provided context
- Well-structured and easy to understand
- Professional but accessible
- Focused on actionable insights when possible
- Clear about limitations if information is incomplete

If the context doesn't contain enough information to answer the question, say so clearly."""

            user_prompt = f"""Context from economic research documents:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above. If specific data or statistics are mentioned, include them in your response. If the context doesn't fully address the question, clearly state what information is missing."""

            response = self.openai_client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating OpenAI answer: {str(e)}")
            return self._generate_fallback_answer(context)
    
    def _generate_fallback_answer(self, context: str) -> str:
        """Generate a fallback answer when LLM is not available"""
        if not context:
            return "I couldn't find relevant information to answer your question."
        
        # Simple extractive approach - return relevant context with some formatting
        lines = context.split('\n')
        relevant_lines = [line.strip() for line in lines if line.strip() and not line.startswith('[Source')]
        
        if relevant_lines:
            preview = ' '.join(relevant_lines[:3])  # Take first few sentences
            if len(preview) > 500:
                preview = preview[:500] + "..."
            
            return f"Based on the available documents: {preview}\n\n(Note: This is a simplified response. For more detailed analysis, please ensure the AI service is properly configured.)"
        
        return "I found some relevant information but couldn't generate a detailed response. Please check the system configuration."
    
    async def _format_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format source information for the response"""
        sources = []
        
        seen_docs = set()  # To avoid duplicate documents
        
        for chunk in chunks:
            document = chunk.get('documents', {})
            doc_id = document.get('id')
            
            if doc_id not in seen_docs:
                sources.append({
                    "document_id": doc_id,
                    "title": document.get('title', 'Unknown Document'),
                    "filename": document.get('filename', ''),
                    "page_number": chunk.get('page_number'),
                    "relevance_score": chunk.get('similarity_score', 0.0)
                })
                seen_docs.add(doc_id)
        
        # Sort by relevance score
        sources.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return sources
    
    def _calculate_confidence(self, chunks: List[Dict[str, Any]], answer: str) -> float:
        """Calculate confidence score for the response"""
        if not chunks:
            return 0.0
        
        # Basic confidence calculation based on:
        # 1. Number of relevant chunks found
        # 2. Average similarity scores
        # 3. Answer length (longer answers might indicate more comprehensive info)
        
        avg_similarity = sum(chunk.get('similarity_score', 0.0) for chunk in chunks) / len(chunks)
        
        # Normalize factors
        chunk_count_factor = min(len(chunks) / 3.0, 1.0)  # Diminishing returns after 3 chunks
        similarity_factor = max(0.0, min(avg_similarity, 1.0))  # Ensure between 0 and 1
        answer_length_factor = min(len(answer) / 200.0, 1.0)  # Normalize based on typical answer length
        
        # Weight the factors
        confidence = (
            similarity_factor * 0.5 +
            chunk_count_factor * 0.3 +
            answer_length_factor * 0.2
        )
        
        return round(confidence, 2)
    
    async def get_available_documents(self) -> List[Dict[str, Any]]:
        """Get list of available documents in the system"""
        try:
            documents = await db_service.list_documents()
            return documents
        except Exception as e:
            logger.error(f"Error getting available documents: {str(e)}")
            return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of the RAG system components"""
        embedding_info = embedding_service.get_model_info()
        
        return {
            "embedding_service": {
                "status": "available",
                "model": embedding_info["model_name"],
                "provider": embedding_info["provider"],
                "dimensions": embedding_info["embedding_dimension"]
            },
            "llm_service": {
                "status": "available" if (self.gemini_client or self.openai_client) else "unavailable",
                "model": self.llm_model if (self.gemini_client or self.openai_client) else None,
                "provider": "gemini" if self.gemini_client else ("openai" if self.openai_client else None)
            },
            "database_service": {
                "status": "available"  # Assuming it's available if we got this far
            }
        }

# Singleton instance
rag_service = RAGService() 