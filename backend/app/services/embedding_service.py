import os
import openai
from typing import List, Dict, Any
import asyncio
import numpy as np
# from sentence_transformers import SentenceTransformer
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
            # Fallback to simple word-based embeddings
            self.embedding_model = "simple-word-embeddings"
            self.embedding_dim = 384
            logger.info("Using simple word-based embeddings (fallback)")
    
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
            return await self._generate_simple_embedding(text)
    
    async def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        if self.gemini_client:
            return await self._generate_gemini_batch_embeddings(texts)
        elif self.openai_client:
            return await self._generate_openai_batch_embeddings(texts)
        else:
            return await self._generate_simple_batch_embeddings(texts)
    
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
    
    async def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate simple word-based embedding as fallback"""
        try:
            text = self._preprocess_text(text)
            
            # Simple hash-based embedding as absolute fallback
            words = text.lower().split()
            embedding = [0.0] * self.embedding_dim
            
            for i, word in enumerate(words[:100]):  # Limit to 100 words
                hash_val = hash(word) % self.embedding_dim
                embedding[hash_val] += 1.0
            
            # Normalize
            magnitude = sum(x*x for x in embedding) ** 0.5
            if magnitude > 0:
                embedding = [x/magnitude for x in embedding]
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating simple embedding: {str(e)}")
            return [0.0] * self.embedding_dim
    
    async def _generate_simple_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate batch simple embeddings"""
        embeddings = []
        for text in texts:
            embedding = await self._generate_simple_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text before generating embeddings"""
        if not text or not isinstance(text, str):
            return ""
        
        # Clean and limit text length
        text = text.strip()
        
        # Limit to reasonable length for API calls (8000 chars for Gemini)
        if len(text) > 8000:
            text = text[:8000]
        
        # Remove excessive whitespace
        import re
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays for calculation
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            magnitude1 = np.linalg.norm(vec1)
            magnitude2 = np.linalg.norm(vec2)
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            
            similarity = dot_product / (magnitude1 * magnitude2)
            return float(similarity)
        
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding specifically for search queries"""
        try:
            # Use the same embedding generation method
            return await self.generate_embedding(query)
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            def _generate_sync():
                # Simplified fallback for queries
                return [0.0] * self.embedding_dim
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, _generate_sync)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        return {
            "model_name": self.embedding_model,
            "embedding_dimension": self.embedding_dim,
            "provider": "gemini" if self.gemini_client else "openai" if self.openai_client else "simple",
            "status": "active"
        }

# Singleton instance
embedding_service = EmbeddingService() 