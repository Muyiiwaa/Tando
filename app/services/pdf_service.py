from typing import Optional
from PyPDF2 import PdfReader
from fastapi import UploadFile
from io import BytesIO

class PDFService:
    async def extract_text(self, file: UploadFile) -> Optional[str]:
        """
        Extract text from a PDF file.
        
        Args:
            file: UploadFile object containing the PDF
            
        Returns:
            str: Extracted text from the PDF
            
        Raises:
            ValueError: If file is not a valid PDF
        """
        try:
            # Read the uploaded file into memory
            content = await file.read()
            pdf_file = BytesIO(content)
            
            # Create PDF reader object
            reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            raise ValueError(f"Error processing PDF: {str(e)}") 