import os
import logging
from datetime import datetime
from typing import Dict, Any

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ml_api.log'),
            logging.StreamHandler()
        ]
    )

def ensure_directories():
    """Ensure required directories exist"""
    directories = [
        'data/uploads',
        'data/processed',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def validate_file_size(file_size: int, max_size: int = 50 * 1024 * 1024) -> bool:
    """Validate file size"""
    return file_size <= max_size

def format_bytes(bytes_size: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()

def clean_filename(filename: str) -> str:
    """Clean filename for safe storage"""
    import re
    # Remove special characters and spaces
    cleaned = re.sub(r'[^\w\-_\.]', '_', filename)
    # Remove multiple underscores
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned

def generate_response_metadata(processing_time: float, model_used: str, input_size: int) -> Dict[str, Any]:
    """Generate response metadata"""
    return {
        'processing_time_seconds': round(processing_time, 3),
        'model_used': model_used,
        'input_size_chars': input_size,
        'timestamp': datetime.utcnow().isoformat(),
        'api_version': '1.0.0'
    }