# Technical Approach

## System Architecture

This RAG (Retrieval-Augmented Generation) system is designed as a scalable, production-ready solution for economic research queries using Alberta business data.

### Core Components

1. **Document Processing Pipeline**
   - PDF text extraction using PyMuPDF
   - Intelligent chunking with section-aware splitting
   - Metadata preservation for source attribution

2. **Vector Embeddings**
   - **Primary**: Google Gemini API `text-embedding-004` (768 dimensions) - **FREE**
   - **Fallback**: OpenAI `text-embedding-3-small` (1536 dimensions)
   - **Local**: Sentence Transformers `all-MiniLM-L6-v2` (384 dimensions)

3. **Vector Database**
   - Supabase with pgvector extension
   - Optimized similarity search with cosine distance
   - Efficient indexing for sub-second query response

4. **RAG Pipeline**
   - Semantic query processing with task-specific prefixes
   - Context-aware retrieval with relevance scoring
   - LLM integration with specialized prompts for economic research

5. **API Architecture**
   - FastAPI with async/await for high performance
   - RESTful endpoints for chat and document management
   - Comprehensive error handling and logging

### Key Design Decisions

- **100% Free Stack**: Complete RAG system using Google's free Gemini API for both embeddings and LLM
- **Intelligent Chunking**: Custom algorithm that respects document structure rather than fixed-size splitting
- **Graceful Fallbacks**: Multi-tier fallback system ensures system availability
- **Source Attribution**: Maintains complete provenance for research integrity
- **Confidence Scoring**: Provides transparency about answer quality

### Technology Stack

- **Backend**: FastAPI + Python 3.9+
- **Database**: Supabase (PostgreSQL + pgvector)
- **Embeddings**: Google Gemini API (Free)
- **LLM**: Google Gemini 2.0 Flash (Free)
- **Document Processing**: PyMuPDF
- **Frontend**: Next.js + TypeScript (planned)

### Performance Optimizations

- Batch embedding generation for efficiency
- Vector similarity indexing for fast retrieval
- Async processing throughout the pipeline
- Intelligent text preprocessing and chunking

This approach ensures both technical excellence and practical usability for Alberta business research needs.
