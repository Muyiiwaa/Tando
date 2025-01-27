from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

class YouTubeService:
    async def get_transcript(self, url: str) -> str:
        """Extract transcript from YouTube video URL"""
        try:
            # Extract video ID from URL
            video_id = re.findall(
                r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
                url
            )[0]
            
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = TextFormatter()
            text = formatter.format_transcript(transcript_list)
            return text.strip()
        except Exception as e:
            raise ValueError(f"Error extracting YouTube transcript: {str(e)}") 