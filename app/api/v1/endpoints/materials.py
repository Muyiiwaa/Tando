from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_active_user, get_async_db
from app.models.user import User
from app.models.material import Material  # Import Material model from models
from app.schemas.material import MaterialCreate, MaterialResponse
from app.schemas.ai_content import Flashcard, MultipleChoiceQuestion
from app.services.material_parser import MaterialParser
from app.services.ai_generator import AIGenerator
from app.services.pdf_service import PDFService
from app.services.youtube_service import YouTubeService

router = APIRouter()
ai_generator = AIGenerator()
pdf_service = PDFService()
youtube_service = YouTubeService()

@router.post(
    "/upload/pdf",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Error processing PDF: Invalid file format"}
                }
            }
        }
    }
)
async def upload_pdf(
    file: UploadFile = File(...),
    title: str = Form(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload PDF learning material
    
    - **file**: PDF file (must be a valid PDF)
    - **title**: Title of the material
    
    Example curl command:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/materials/upload/pdf" \
      -H "Authorization: Bearer your_token" \
      -F "file=@path/to/your/document.pdf" \
      -F "title=Your Document Title"
    ```
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF"
        )
    
    try:
        content = await pdf_service.extract_text(file)
        
        # Create the model instance directly
        material = Material(
            title=title,
            content=content,
            source_type="pdf",
            source_url=None,
            owner_id=current_user.id
        )
        
        db.add(material)
        await db.commit()
        await db.refresh(material)
        
        return material
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post(
    "/upload/youtube",
    response_model=MaterialResponse,
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid YouTube URL"}
                }
            }
        }
    }
)
async def upload_youtube(
    youtube_url: str = Form(...),
    title: str = Form(...),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload YouTube video transcript
    
    - **youtube_url**: Valid YouTube video URL (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)
    - **title**: Title of the material
    
    Example curl command:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/materials/upload/youtube" \
      -H "Authorization: Bearer your_token" \
      -F "youtube_url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" \
      -F "title=Your Video Title"
    ```
    """
    try:
        content = await youtube_service.get_transcript(youtube_url)
        
        material_create = MaterialCreate(
            title=title,
            content=content,
            source_type="youtube",
            source_url=youtube_url
        )
        
        material = Material(
            **material_create.model_dump(),
            owner_id=current_user.id
        )
        
        db.add(material)
        await db.commit()
        await db.refresh(material)
        
        return material
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{material_id}/generate-flashcards", response_model=List[Flashcard])
async def generate_flashcards(
    material_id: int,
    num_cards: int = 5,
    topics: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    material = await db.get(Material, material_id)
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    flashcards = await ai_generator.generate_flashcards(
        material.content,
        num_cards,
        topics
    )
    return flashcards

@router.post("/{material_id}/generate-questions", response_model=List[MultipleChoiceQuestion])
async def generate_questions(
    material_id: int,
    num_questions: int = 5,
    topics: Optional[List[str]] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    material = await db.get(Material, material_id)
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    questions = await ai_generator.generate_questions(
        material.content,
        num_questions,
        topics
    )
    return questions 