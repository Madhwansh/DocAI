import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8000
    
    # Model Configuration
    SUMMARIZATION_MODEL = "facebook/bart-large-cnn"
    LONG_FORM_MODEL = "microsoft/DialoGPT-large"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    
    # File Upload Configuration
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR = "data/uploads"
    PROCESSED_DIR = "data/processed"
    
    # YouTube Configuration
    MAX_VIDEO_DURATION = 3600  # 1 hour in seconds
    
    # Device Configuration
    DEVICE = "cuda" if os.getenv("CUDA_AVAILABLE", "false").lower() == "true" else "cpu"
    
    # Hugging Face Token (optional, for private models)
    HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN", None)