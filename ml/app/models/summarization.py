from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch
from config.settings import Settings
import logging

logger = logging.getLogger(__name__)

class SummarizationModels:
    def __init__(self):
        self.device = Settings.DEVICE
        self.models = {}
        self.tokenizers = {}
        self._load_models()
    
    def _load_models(self):
        """Load all summarization models"""
        try:
            # BART Large CNN - Best for news/article summarization
            self._load_bart_model()
            
            # T5 Small - Good balance of speed and quality
            self._load_t5_model()
            
            # LED (Longformer Encoder-Decoder) - Best for long documents
            self._load_led_model()
            
            # Pegasus - Excellent for research papers
            self._load_pegasus_model()
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def _load_bart_model(self):
        """Load BART model for general summarization"""
        model_name = "facebook/bart-large-cnn"
        self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
        self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        logger.info(f"Loaded {model_name}")
    
    def _load_t5_model(self):
        """Load T5 model for fast summarization"""
        model_name = "t5-small"
        self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
        self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        logger.info(f"Loaded {model_name}")
    
    def _load_led_model(self):
        """Load LED model for long document summarization"""
        model_name = "allenai/led-base-16384"
        self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
        self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        logger.info(f"Loaded {model_name}")
    
    def _load_pegasus_model(self):
        """Load Pegasus model for research paper summarization"""
        model_name = "google/pegasus-xsum"
        self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_name)
        self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        logger.info(f"Loaded {model_name}")
    
    def summarize_with_bart(self, text: str, max_length: int = 500, format_tags: bool = True) -> str:
        """Summarize using BART - Best for news articles and general content"""
        model_name = "facebook/bart-large-cnn"
        return self._generate_summary(text, model_name, max_length, format_tags)
    
    def summarize_with_t5(self, text: str, max_length: int = 500, format_tags: bool = True) -> str:
        """Summarize using T5 - Fast and efficient"""
        model_name = "t5-small"
        # T5 requires task prefix
        text = f"summarize: {text}"
        return self._generate_summary(text, model_name, max_length, format_tags)
    
    def summarize_with_led(self, text: str, max_length: int = 500, format_tags: bool = True) -> str:
        """Summarize using LED - Best for long documents (up to 16K tokens)"""
        model_name = "allenai/led-base-16384"
        return self._generate_summary(text, model_name, max_length, format_tags)
    
    def summarize_with_pegasus(self, text: str, max_length: int = 500, format_tags: bool = True) -> str:
        """Summarize using Pegasus - Best for research papers"""
        model_name = "google/pegasus-xsum"
        return self._generate_summary(text, model_name, max_length, format_tags)
    
    def _generate_summary(self, text: str, model_name: str, max_length: int, format_tags: bool) -> str:
        """Generate summary using specified model"""
        try:
            tokenizer = self.tokenizers[model_name]
            model = self.models[model_name]
            
            # Tokenize input
            inputs = tokenizer.encode(
                text, 
                return_tensors="pt", 
                max_length=1024, 
                truncation=True
            ).to(self.device)
            
            # Generate summary
            with torch.no_grad():
                summary_ids = model.generate(
                    inputs, 
                    max_length=max_length, 
                    min_length=50,
                    num_beams=4,
                    length_penalty=2.0,
                    early_stopping=True
                )
            
            # Decode summary
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            
            if format_tags:
                summary = self._format_with_tags(summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary with {model_name}: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _format_with_tags(self, summary: str) -> str:
        """Format summary with HTML-like tags for better structure"""
        sentences = summary.split('. ')
        if len(sentences) <= 1:
            return f"<summary>{summary}</summary>"
        
        # Create structured summary
        formatted = "<summary>\n"
        
        # Main summary
        formatted += f"<main>{sentences[0]}.</main>\n"
        
        # Key points
        if len(sentences) > 1:
            formatted += "<key_points>\n"
            for i, sentence in enumerate(sentences[1:], 1):
                if sentence.strip():
                    formatted += f"<point_{i}>{sentence.strip()}{'.' if not sentence.endswith('.') else ''}</point_{i}>\n"
            formatted += "</key_points>\n"
        
        formatted += "</summary>"
        return formatted
    
    def get_best_model_for_content_type(self, content_type: str) -> str:
        """Return the best model for specific content type"""
        model_recommendations = {
            "research_paper": "google/pegasus-xsum",
            "news_article": "facebook/bart-large-cnn",
            "long_document": "allenai/led-base-16384",
            "general": "facebook/bart-large-cnn",
            "fast": "t5-small"
        }
        return model_recommendations.get(content_type, "facebook/bart-large-cnn")