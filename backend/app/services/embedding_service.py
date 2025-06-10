import os
import openai
from typing import List, Dict, Any
import asyncio
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.gemini_client = None
        self.openai_client = None
        self.local_model = None
        
        # Try to initialize Gemini first (free tier available)
        if GEMINI_AVAILABLE and self._initialize_gemini():
            self.embedding_model = "models/text-embedding-004"
            self.embedding_dim = 768
            logger.info("Using Google Gemini embeddings (free tier)")
        elif self._initialize_openai():
            self.embedding_model = "text-embedding-3-small"
            self.embedding_dim = 1536
            logger.info("Using OpenAI embeddings")
        else:
            # Fallback to local sentence transformers (completely free)
            self.local_model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_model = "all-MiniLM-L6-v2"
            self.embedding_dim = 384
            logger.info("Using local sentence transformers (completely free)")
    
    def _initialize_gemini(self) -> bool:
        """Initialize Google Gemini API"""
        try:
            # Try both GOOGLE_API_KEY and GEMINI_API_KEY for flexibility
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GOOGLE_API_KEY or GEMINI_API_KEY not set")
                return False
            
            # Initialize the Gemini API
            genai.configure(api_key=api_key)
            self.gemini_client = True
            return True
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini API: {str(e)}")
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
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        if self.gemini_client:
            return await self._generate_gemini_embedding(text)
        elif self.openai_client:
            return await self._generate_openai_embedding(text)
        else:
            return await self._generate_local_embedding(text)
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if self.gemini_client:
            return await self._generate_gemini_batch_embeddings(texts)
        elif self.openai_client:
            return await self._generate_openai_batch_embeddings(texts)
        else:
            return await self._generate_local_batch_embeddings(texts)
    
    async def _generate_gemini_embedding(self, text: str) -> List[float]:
        """Generate embedding using Google Gemini API"""
        try:
            # Clean and truncate text if too long
            text = self._preprocess_text(text)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            def _generate_sync():
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                return result['embedding']
            
            embedding = await loop.run_in_executor(None, _generate_sync)
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating Gemini embedding: {str(e)}")
            # Fallback to OpenAI if available
            if self.openai_client:
                return await self._generate_openai_embedding(text)
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def _generate_gemini_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate batch embeddings using Google Gemini API"""
        try:
            # Preprocess all texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Gemini API doesn't have native batch support, so process individually
            embeddings = []
            for text in processed_texts:
                try:
                    embedding = await self._generate_gemini_embedding(text)
                    embeddings.append(embedding)
                    # Small delay to respect rate limits
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error generating embedding for text: {str(e)}")
                    # Use zero vector as fallback
                    embeddings.append([0.0] * self.embedding_dim)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating Gemini batch embeddings: {str(e)}")
            # Fallback to individual processing
            embeddings = []
            for text in texts:
                try:
                    embedding = await self._generate_gemini_embedding(text)
                    embeddings.append(embedding)
                except:
                    # Use zero vector as fallback
                    embeddings.append([0.0] * self.embedding_dim)
            return embeddings

    async def _generate_openai_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            # Clean and truncate text if too long
            text = self._preprocess_text(text)
            
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def _generate_openai_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate batch embeddings using OpenAI API"""
        try:
            # Preprocess all texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # OpenAI supports batch processing
            response = self.openai_client.embeddings.create(
                input=processed_texts,
                model=self.embedding_model
            )
            
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error generating OpenAI batch embeddings: {str(e)}")
            # Fallback to individual processing if batch fails
            embeddings = []
            for text in texts:
                try:
                    embedding = await self._generate_openai_embedding(text)
                    embeddings.append(embedding)
                except:
                    # Use zero vector as fallback
                    embeddings.append([0.0] * self.embedding_dim)
            return embeddings
    
    async def _generate_local_embedding(self, text: str) -> List[float]:
        """Generate embedding using local sentence transformer"""
        try:
            text = self._preprocess_text(text)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                lambda: self.local_model.encode(text, convert_to_tensor=False)
            )
            
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating local embedding: {str(e)}")
            raise Exception(f"Failed to generate embedding: {str(e)}")
    
    async def _generate_local_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate batch embeddings using local sentence transformer"""
        try:
            processed_texts = [self._preprocess_text(text) for text in texts]
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, 
                lambda: self.local_model.encode(processed_texts, convert_to_tensor=False)
            )
            
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating local batch embeddings: {str(e)}")
            raise Exception(f"Failed to generate batch embeddings: {str(e)}")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before embedding generation"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Truncate based on the provider
        if self.gemini_client:
            # Gemini text-embedding-004 has ~20,000 character limit
            max_chars = 19000  # Conservative estimate
        elif self.openai_client:
            # OpenAI has 8191 token limit for text-embedding-3-small
            # Rough estimate: 1 token ≈ 4 characters
            max_chars = 8000 * 4  # Conservative estimate
        else:
            # Local models typically have smaller limits
            max_chars = 512 * 4
        
        if len(text) > max_chars:
            text = text[:max_chars]
        
        return text
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding specifically for search queries"""
        if self.gemini_client:
            # For Gemini, we'll use the task_type parameter instead of prefix
            text = self._preprocess_text(query)
            loop = asyncio.get_event_loop()
            
            def _generate_sync():
                result = genai.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_query"  # Specific task type for queries
                )
                return result['embedding']
            
            return await loop.run_in_executor(None, _generate_sync)
        else:
            # Generic prefix for other providers
            query = f"search query: {query}"
            return await self.generate_embedding(query)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        if self.gemini_client:
            provider = "gemini"
        elif self.openai_client:
            provider = "openai"
        else:
            provider = "local"
            
        return {
            "model_name": self.embedding_model,
            "embedding_dimension": self.embedding_dim,
            "provider": provider
        }

# Singleton instance
embedding_service = EmbeddingService() 