from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.summarization import SummarizationModels
from app.services.pdf_processor import PDFProcessor
from app.services.youtube_processor import YouTubeProcessor
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
summarization_models = SummarizationModels()
pdf_processor = PDFProcessor()
youtube_processor = YouTubeProcessor()

# Request models
class TextSummarizationRequest(BaseModel):
    text: str
    max_length: Optional[int] = 500
    format_with_tags: Optional[bool] = True
    model_type: Optional[str] = "auto"  # auto, bart, t5, led, pegasus

class YouTubeSummarizationRequest(BaseModel):
    url: str
    max_length: Optional[int] = 500
    format_with_tags: Optional[bool] = True

@router.post("/summarize/text")
async def summarize_text(request: TextSummarizationRequest):
    """Summarize plain text using the best available model"""
    try:
        # Choose model based on request or auto-detect
        if request.model_type == "auto":
            # Auto-detect best model based on text length and content
            if len(request.text) > 8000:
                model_method = summarization_models.summarize_with_led
            elif "research" in request.text.lower() or "study" in request.text.lower():
                model_method = summarization_models.summarize_with_pegasus
            else:
                model_method = summarization_models.summarize_with_bart
        else:
            model_methods = {
                "bart": summarization_models.summarize_with_bart,
                "t5": summarization_models.summarize_with_t5,
                "led": summarization_models.summarize_with_led,
                "pegasus": summarization_models.summarize_with_pegasus
            }
            model_method = model_methods.get(request.model_type, summarization_models.summarize_with_bart)
        
        # Generate summary
        summary = model_method(
            request.text, 
            request.max_length, 
            request.format_with_tags
        )
        
        return {
            "success": True,
            "summary": summary,
            "model_used": request.model_type,
            "input_length": len(request.text),
            "summary_length": len(summary)
        }
        
    except Exception as e:
        logger.error(f"Error in text summarization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize/pdf")
async def summarize_pdf(file: UploadFile = File(...), max_length: int = 500, format_with_tags: bool = True):
    """Extract text from PDF and generate summary"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Extract text from PDF
        pdf_result = await pdf_processor.extract_text_from_pdf(file)
        
        if not pdf_result['success']:
            raise HTTPException(status_code=400, detail=pdf_result['error'])
        
        text = pdf_result['text']
        metadata = pdf_result['metadata']
        
        # Detect document type for optimal model selection
        doc_type = pdf_processor.detect_document_type(text, metadata)
        
        # Choose appropriate model
        if doc_type == 'research_paper':
            summary = summarization_models.summarize_with_pegasus(text, max_length, format_with_tags)
        elif doc_type == 'long_document':
            summary = summarization_models.summarize_with_led(text, max_length, format_with_tags)
        else:
            summary = summarization_models.summarize_with_bart(text, max_length, format_with_tags)
        
        return {
            "success": True,
            "summary": summary,
            "document_type": doc_type,
            "metadata": metadata,
            "file_info": pdf_result['file_info'],
            "model_used": {
                'research_paper': 'pegasus',
                'long_document': 'led',
                'general': 'bart'
            }.get(doc_type, 'bart')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in PDF summarization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize/youtube")
async def summarize_youtube(request: YouTubeSummarizationRequest):
    """Extract transcript from YouTube video and generate summary with insights"""
    try:
        # Process YouTube video
        video_result = await youtube_processor.process_youtube_video(request.url)
        
        if not video_result['success']:
            raise HTTPException(status_code=400, detail=video_result['error'])
        
        transcript = video_result['transcript']
        metadata = video_result['metadata']
        content_type = video_result['content_type']
        
        # Choose appropriate model based on content type
        if content_type == 'technical':
            summary = summarization_models.summarize_with_pegasus(transcript, request.max_length, request.format_with_tags)
            model_used = 'pegasus'
        elif content_type == 'educational':
            summary = summarization_models.summarize_with_bart(transcript, request.max_length, request.format_with_tags)
            model_used = 'bart'
        elif len(transcript) > 8000:
            summary = summarization_models.summarize_with_led(transcript, request.max_length, request.format_with_tags)
            model_used = 'led'
        else:
            summary = summarization_models.summarize_with_bart(transcript, request.max_length, request.format_with_tags)
            model_used = 'bart'
        
        # Get video insights
        insights = youtube_processor.get_video_insights(metadata, transcript)
        
        return {
            "success": True,
            "summary": summary,
            "video_metadata": metadata,
            "content_type": content_type,
            "insights": insights,
            "model_used": model_used,
            "transcript_length": len(transcript)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in YouTube summarization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/info")
async def get_models_info():
    """Get information about available models and their use cases"""
    return {
        "available_models": {
            "facebook/bart-large-cnn": {
                "name": "BART Large CNN",
                "best_for": "News articles, general content, web articles",
                "max_input_length": "1024 tokens",
                "speed": "Medium",
                "quality": "High"
            },
            "t5-small": {
                "name": "T5 Small",
                "best_for": "Fast summarization, short texts",
                "max_input_length": "512 tokens",
                "speed": "Fast",
                "quality": "Medium"
            },
            "allenai/led-base-16384": {
                "name": "LED (Longformer Encoder-Decoder)",
                "best_for": "Long documents, research papers, books",
                "max_input_length": "16384 tokens",
                "speed": "Slow",
                "quality": "Very High"
            },
            "google/pegasus-xsum": {
                "name": "Pegasus XSum",
                "best_for": "Research papers, scientific content, technical documents",
                "max_input_length": "1024 tokens",
                "speed": "Medium",
                "quality": "Very High"
            }
        },
        "use_case_recommendations": {
            "research_paper": "google/pegasus-xsum",
            "news_article": "facebook/bart-large-cnn",
            "long_document": "allenai/led-base-16384",
            "user_manual": "allenai/led-base-16384",
            "youtube_educational": "facebook/bart-large-cnn",
            "youtube_technical": "google/pegasus-xsum",
            "general": "facebook/bart-large-cnn",
            "fast_processing": "t5-small"
        }
    }