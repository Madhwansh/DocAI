# DocAI ML Service

A FastAPI-based machine learning service for document and video summarization using state-of-the-art Hugging Face models.

## Features

- **Multi-Model Support**: BART, T5, LED, and Pegasus models for different use cases
- **PDF Processing**: Extract and summarize research papers, manuals, and documents
- **YouTube Processing**: Extract transcripts and summarize video content
- **Smart Model Selection**: Automatically chooses the best model based on content type
- **Formatted Output**: Structured summaries with HTML-like tags
- **Content Type Detection**: Identifies research papers, manuals, educational content, etc.

## Available Models

1. **BART Large CNN** - Best for news articles and general content
2. **T5 Small** - Fast processing for shorter texts
3. **LED (Longformer)** - Excellent for long documents (up to 16K tokens)
4. **Pegasus XSum** - Optimized for research papers and technical content

## Installation

```bash
cd ml
pip install -r requirements.txt
```

## Usage

### Start the API server
```bash
python main.py
```

### API Endpoints

- `POST /api/v1/summarize/text` - Summarize plain text
- `POST /api/v1/summarize/pdf` - Upload and summarize PDF files
- `POST /api/v1/summarize/youtube` - Summarize YouTube videos
- `GET /api/v1/models/info` - Get model information

### Example Requests

#### Text Summarization
```python
import requests

response = requests.post("http://localhost:8000/api/v1/summarize/text", 
    json={
        "text": "Your long text here...",
        "max_length": 500,
        "format_with_tags": True,
        "model_type": "auto"
    }
)
```

#### PDF Summarization
```python
files = {"file": open("document.pdf", "rb")}
response = requests.post("http://localhost:8000/api/v1/summarize/pdf", files=files)
```

#### YouTube Summarization
```python
response = requests.post("http://localhost:8000/api/v1/summarize/youtube",
    json={
        "url": "https://youtube.com/watch?v=VIDEO_ID",
        "max_length": 500
    }
)
```

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.