from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.api.summarization import router as summarization_router
from app.utils.helpers import setup_logging, ensure_directories
from config.settings import Settings
import logging

# Setup logging and directories
setup_logging()
ensure_directories()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="DocAI ML API",
    description="Advanced ML API for document and video summarization using state-of-the-art models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(summarization_router, prefix="/api/v1", tags=["summarization"])

@app.get("/")
async def root():
    return {
        "message": "DocAI ML API is running!",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "ml-api",
        "models_loaded": "true"
    }

@app.get("/api/v1/info")
async def api_info():
    """Get API information and capabilities"""
    return {
        "service": "DocAI ML API",
        "version": "1.0.0",
        "capabilities": {
            "text_summarization": True,
            "pdf_processing": True,
            "youtube_processing": True,
            "multi_model_support": True,
            "formatted_output": True
        },
        "supported_models": [
            "facebook/bart-large-cnn",
            "t5-small", 
            "allenai/led-base-16384",
            "google/pegasus-xsum"
        ],
        "endpoints": {
            "text_summarization": "/api/v1/summarize/text",
            "pdf_summarization": "/api/v1/summarize/pdf",
            "youtube_summarization": "/api/v1/summarize/youtube",
            "models_info": "/api/v1/models/info"
        }
    }

if __name__ == "__main__":
    logger.info("Starting DocAI ML API...")
    uvicorn.run(
        app, 
        host=Settings.API_HOST, 
        port=Settings.API_PORT,
        reload=True
    )