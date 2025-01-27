from typing import Optional
from PyPDF2 import PdfReader
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from fastapi import UploadFile, HTTPException
import re
from io import BytesIO

class MaterialParser:
    @staticmethod
    async def parse_pdf(file: UploadFile) -> str:
        try:
            content = await file.read()
            pdf = PdfReader(BytesIO(content))
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error parsing PDF: {str(e)}"
            )

    @staticmethod
    def parse_youtube_url(url: str) -> str:
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
            raise HTTPException(
                status_code=400,
                detail=f"Error extracting YouTube transcript: {str(e)}"
            ) 