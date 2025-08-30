from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import re
import logging
from typing import Dict, Any, List
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class YouTubeProcessor:
    def __init__(self):
        self.max_duration = 3600  # 1 hour limit
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("Invalid YouTube URL format")
    
    async def process_youtube_video(self, url: str) -> Dict[str, Any]:
        """Process YouTube video and extract transcript"""
        try:
            # Extract video ID
            video_id = self.extract_video_id(url)
            
            # Get video metadata using pytube
            yt = YouTube(url)
            
            # Check duration
            if yt.length > self.max_duration:
                return {
                    'success': False,
                    'error': f'Video too long: {yt.length} seconds (max: {self.max_duration})',
                    'transcript': '',
                    'metadata': {}
                }
            
            # Extract metadata
            metadata = {
                'title': yt.title,
                'author': yt.author,
                'duration': yt.length,
                'views': yt.views,
                'description': yt.description,
                'publish_date': yt.publish_date.isoformat() if yt.publish_date else None,
                'video_id': video_id,
                'thumbnail': yt.thumbnail_url
            }
            
            # Get transcript
            transcript_data = self._get_transcript(video_id)
            
            if not transcript_data['success']:
                return {
                    'success': False,
                    'error': transcript_data['error'],
                    'transcript': '',
                    'metadata': metadata
                }
            
            # Process and clean transcript
            cleaned_transcript = self._process_transcript(transcript_data['transcript'])
            
            return {
                'success': True,
                'transcript': cleaned_transcript,
                'metadata': metadata,
                'content_type': self._detect_video_type(metadata, cleaned_transcript)
            }
            
        except Exception as e:
            logger.error(f"Error processing YouTube video: {e}")
            return {
                'success': False,
                'error': str(e),
                'transcript': '',
                'metadata': {}
            }
    
    def _get_transcript(self, video_id: str) -> Dict[str, Any]:
        """Get transcript using YouTube Transcript API"""
        try:
            # Try to get transcript in preferred order
            languages = ['en', 'en-US', 'en-GB']
            transcript = None
            
            for lang in languages:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                    break
                except:
                    continue
            
            # If no specific language found, get any available transcript
            if not transcript:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for transcript_info in transcript_list:
                    if transcript_info.is_generated or transcript_info.is_translatable:
                        transcript = transcript_info.fetch()
                        break
            
            if not transcript:
                return {
                    'success': False,
                    'error': 'No transcript available for this video',
                    'transcript': []
                }
            
            return {
                'success': True,
                'transcript': transcript,
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error fetching transcript: {str(e)}',
                'transcript': []
            }
    
    def _process_transcript(self, transcript: List[Dict]) -> str:
        """Process raw transcript into clean text"""
        if not transcript:
            return ""
        
        # Combine all transcript entries
        full_text = ""
        for entry in transcript:
            text = entry.get('text', '').strip()
            if text:
                # Clean up common transcript artifacts
                text = re.sub(r'\[.*?\]', '', text)  # Remove [Music], [Applause], etc.
                text = re.sub(r'\(.*?\)', '', text)  # Remove (inaudible), etc.
                text = text.replace('\n', ' ')
                full_text += text + " "
        
        # Clean up the full text
        full_text = re.sub(r'\s+', ' ', full_text)  # Multiple spaces to single
        full_text = full_text.strip()
        
        # Add periods to sentences that don't end with punctuation
        sentences = full_text.split('.')
        cleaned_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and not sentence.endswith(('.', '!', '?')):
                sentence += '.'
            if sentence:
                cleaned_sentences.append(sentence)
        
        return ' '.join(cleaned_sentences)
    
    def _detect_video_type(self, metadata: Dict, transcript: str) -> str:
        """Detect the type of video content for optimal summarization"""
        title_lower = metadata.get('title', '').lower()
        description_lower = metadata.get('description', '').lower()
        transcript_lower = transcript.lower()
        
        # Educational content indicators
        educational_indicators = [
            'tutorial', 'how to', 'learn', 'course', 'lesson', 'education',
            'explain', 'guide', 'introduction to', 'basics of'
        ]
        
        # News/documentary indicators
        news_indicators = [
            'news', 'report', 'documentary', 'investigation', 'analysis',
            'breaking', 'update', 'interview'
        ]
        
        # Technical/research indicators
        technical_indicators = [
            'research', 'study', 'paper', 'conference', 'presentation',
            'technical', 'engineering', 'science', 'algorithm'
        ]
        
        # Entertainment indicators
        entertainment_indicators = [
            'funny', 'comedy', 'entertainment', 'music', 'gaming',
            'reaction', 'vlog', 'challenge'
        ]
        
        # Count indicators in title, description, and transcript
        def count_indicators(indicators, text_sources):
            count = 0
            for indicator in indicators:
                for text in text_sources:
                    if indicator in text:
                        count += 1
            return count
        
        text_sources = [title_lower, description_lower, transcript_lower[:1000]]  # First 1000 chars of transcript
        
        educational_score = count_indicators(educational_indicators, text_sources)
        news_score = count_indicators(news_indicators, text_sources)
        technical_score = count_indicators(technical_indicators, text_sources)
        entertainment_score = count_indicators(entertainment_indicators, text_sources)
        
        # Determine video type based on highest score
        scores = {
            'educational': educational_score,
            'news': news_score,
            'technical': technical_score,
            'entertainment': entertainment_score
        }
        
        max_score = max(scores.values())
        if max_score == 0:
            return 'general'
        
        return max(scores, key=scores.get)
    
    def get_video_insights(self, metadata: Dict, transcript: str) -> Dict[str, Any]:
        """Generate insights about the video content"""
        duration_minutes = metadata.get('duration', 0) / 60
        word_count = len(transcript.split())
        
        insights = {
            'duration_minutes': round(duration_minutes, 2),
            'estimated_reading_time': round(word_count / 200, 2),  # Average reading speed
            'word_count': word_count,
            'content_density': 'high' if word_count / duration_minutes > 150 else 'medium' if word_count / duration_minutes > 100 else 'low',
            'video_type': self._detect_video_type(metadata, transcript)
        }
        
        return insights