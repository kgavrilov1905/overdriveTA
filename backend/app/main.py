import os
from pathlib import Path
# from dotenv import load_dotenv

# # Load environment variables from the project root
# env_path = Path(__file__).parent.parent.parent / ".env"
# load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .routers import chat, documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Alberta Perspectives RAG API",
    description="RAG-powered economic research chatbot for Alberta business insights",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(documents.router)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "Alberta Perspectives RAG API",
        "version": "1.0.0",
        "description": "RAG-powered economic research chatbot for Alberta business insights",
        "endpoints": {
            "chat": "/api/chat",
            "documents": "/api/documents",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "rag-api"
    }

@app.get("/debug-env")
async def debug_env():
    """Debug endpoint to check environment variables."""
    sup_url = os.getenv("SUPABASE_URL")
    sup_key = os.getenv("SUPABASE_ANON_KEY")
    gem_key = os.getenv("GOOGLE_API_KEY")

    return {
        "SUPABASE_URL_SET": "Yes" if sup_url else "No",
        "SUPABASE_URL_LENGTH": len(sup_url) if sup_url else 0,
        "SUPABASE_ANON_KEY_SET": "Yes" if sup_key else "No",
        "SUPABASE_ANON_KEY_LENGTH": len(sup_key) if sup_key else 0,
        "GOOGLE_API_KEY_SET": "Yes" if gem_key else "No",
        "GOOGLE_API_KEY_LENGTH": len(gem_key) if gem_key else 0,
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc) if os.getenv("DEBUG") == "true" else "Internal server error"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
