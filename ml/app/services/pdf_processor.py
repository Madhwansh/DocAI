import PyPDF2
import io
import logging
from typing import Dict, Any
from fastapi import UploadFile

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    async def extract_text_from_pdf(self, file: UploadFile) -> Dict[str, Any]:
        """Extract text content from PDF file"""
        try:
            # Read the uploaded file
            content = await file.read()
            pdf_file = io.BytesIO(content)
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract metadata
            metadata = {
                'num_pages': len(pdf_reader.pages),
                'title': pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                'author': pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown',
                'subject': pdf_reader.metadata.get('/Subject', 'Unknown') if pdf_reader.metadata else 'Unknown'
            }
            
            # Extract text from all pages
            text_content = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                    continue
            
            # Clean and preprocess text
            cleaned_text = self._clean_text(text_content)
            
            return {
                'success': True,
                'text': cleaned_text,
                'metadata': metadata,
                'file_info': {
                    'filename': file.filename,
                    'size': len(content),
                    'content_type': file.content_type
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'metadata': {},
                'file_info': {}
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess extracted text"""
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('---'):  # Remove page markers
                cleaned_lines.append(line)
        
        # Join lines and handle common PDF artifacts
        cleaned_text = ' '.join(cleaned_lines)
        
        # Remove excessive spaces
        import re
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        
        # Remove common PDF artifacts
        cleaned_text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', cleaned_text)
        
        return cleaned_text.strip()
    
    def detect_document_type(self, text: str, metadata: Dict) -> str:
        """Detect the type of document for optimal model selection"""
        text_lower = text.lower()
        title_lower = metadata.get('title', '').lower()
        
        # Research paper indicators
        research_indicators = [
            'abstract', 'introduction', 'methodology', 'results', 'conclusion',
            'references', 'bibliography', 'doi:', 'arxiv', 'journal', 'conference'
        ]
        
        # Manual/documentation indicators
        manual_indicators = [
            'user manual', 'installation', 'configuration', 'setup',
            'troubleshooting', 'faq', 'documentation', 'guide'
        ]
        
        research_score = sum(1 for indicator in research_indicators if indicator in text_lower or indicator in title_lower)
        manual_score = sum(1 for indicator in manual_indicators if indicator in text_lower or indicator in title_lower)
        
        if research_score > manual_score and research_score >= 3:
            return 'research_paper'
        elif manual_score >= 2:
            return 'manual'
        elif len(text) > 10000:  # Long document
            return 'long_document'
        else:
            return 'general'