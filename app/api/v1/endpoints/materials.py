from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.dependencies import get_current_active_user, get_async_db
from app.models.user import User
from app.models.material import Material
from app.models.question import Question
from app.models.flashcard import Flashcard
from app.schemas.material import MaterialCreate, MaterialResponse, MaterialStats, MaterialListItem, MaterialList
from app.schemas.ai_content import Flashcard as FlashcardSchema
from app.schemas.answers import (
    QuestionResponse, MaterialQuestionsResponse,
    FlashcardsResponse, FlashcardDB,
    EvaluationResponse, QuestionAnswerSubmission, QuestionResult
)
from app.services.material_parser import MaterialParser
from app.services.ai_generator import AIGenerator
from app.services.pdf_service import PDFService
from app.services.youtube_service import YouTubeService
from random import sample
from app.services.question_session import QuestionSessionService

router = APIRouter()
ai_generator = AIGenerator()
pdf_service = PDFService()
youtube_service = YouTubeService()
question_session_service = QuestionSessionService()

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

@router.post(
    "/{material_id}/generate-flashcards",
    response_model=List[FlashcardSchema]
)
async def generate_flashcards(
    material_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate or retrieve flashcards for a material"""
    # Check material exists and belongs to user
    material = await db.get(Material, material_id)
    if not material or material.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Material not found")

    # Check if flashcards already exist
    stmt = select(Flashcard).where(
        Flashcard.material_id == material_id,
        Flashcard.user_id == current_user.id
    )
    result = await db.execute(stmt)
    existing_flashcards = result.scalars().all()

    if existing_flashcards:
        return [
            FlashcardSchema(
                id=card.id,
                front=card.front,
                back=card.back
            ) for card in existing_flashcards
        ]

    # Create AI generator instance
    ai_generator = AIGenerator()
    
    # Generate new flashcards
    flashcards = await ai_generator.generate_flashcards(
        material.content,
        num_cards=20
    )

    # Save to database
    for card in flashcards:
        db_flashcard = Flashcard(
            id=card.id,
            front=card.front,
            back=card.back,
            material_id=material_id,
            user_id=current_user.id
        )
        db.add(db_flashcard)
    
    await db.commit()
    return flashcards

@router.get(
    "/{material_id}/flashcards",
    response_model=FlashcardsResponse
)
async def get_flashcards(
    material_id: int,
    num_cards: int = Query(default=10, ge=1, le=20),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieve random flashcards for a material
    
    - **material_id**: ID of the material
    - **num_cards**: Number of flashcards to return (default: 10, max: 20)
    """
    # Verify material exists and user has access
    material = await db.get(Material, material_id)
    if not material or material.owner_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    # Get all flashcards for this material
    stmt = select(Flashcard).where(
        Flashcard.material_id == material_id,
        Flashcard.user_id == current_user.id
    )
    result = await db.execute(stmt)
    flashcards = result.scalars().all()

    if not flashcards:
        raise HTTPException(
            status_code=404,
            detail="No flashcards found for this material"
        )

    # Randomly select requested number of flashcards
    selected_cards = sample(
        flashcards,
        min(num_cards, len(flashcards))
    )

    # Convert to Pydantic models
    flashcard_list = [
        FlashcardDB(
            id=card.id,
            front=card.front,
            back=card.back
        ) for card in selected_cards
    ]

    return FlashcardsResponse(
        flashcards=flashcard_list,
        total_returned=len(flashcard_list)
    )

@router.post("/{material_id}/generate-questions")
async def generate_questions(
    material_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate exactly 20 questions for a material"""
    # Check material exists and belongs to user
    material = await db.get(Material, material_id)
    if not material or material.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Material not found")

    # Check if questions already exist
    stmt = select(Question).where(
        Question.material_id == material_id,
        Question.user_id == current_user.id
    )
    result = await db.execute(stmt)
    existing_questions = result.scalars().all()

    if existing_questions:
        return existing_questions

    # Generate exactly 20 questions
    questions = await ai_generator.generate_questions(
        material.content,
        num_questions=20  # Fixed at 20
    )

    # Save questions to database
    for q in questions:
        db_question = Question(
            id=q.id,
            question_text=q.question,
            options=q.options,
            answer=q.answer,
            explanation=q.explanation,
            category=q.category,
            material_id=material_id,
            user_id=current_user.id
        )
        db.add(db_question)
    
    await db.commit()
    return questions

@router.get(
    "/{material_id}/questions",
    response_model=MaterialQuestionsResponse
)
async def get_material_questions(
    material_id: int,
    num_questions: int = Query(default=5, ge=1, le=20),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retrieve exact number of random questions for a specific material"""
    # Verify material exists and user has access
    material = await db.get(Material, material_id)
    if not material or material.owner_id != current_user.id:
        raise HTTPException(
            status_code=404,
            detail="Material not found"
        )

    # Get all questions
    stmt = select(Question).where(
        Question.material_id == material_id,
        Question.user_id == current_user.id
    )
    result = await db.execute(stmt)
    all_questions = result.scalars().all()

    if not all_questions:
        raise HTTPException(
            status_code=404,
            detail="No questions found for this material. Generate questions first."
        )

    if num_questions > len(all_questions):
        raise HTTPException(
            status_code=400,
            detail=f"Requested {num_questions} questions but only {len(all_questions)} are available"
        )

    # Select random questions and remember their order
    selected_questions = sample(all_questions, num_questions)
    question_order = [all_questions.index(q) for q in selected_questions]

    # Create session to remember question order
    session_id = await question_session_service.create_session(
        material_id=material_id,
        user_id=current_user.id,
        question_order=question_order
    )

    # Format response
    question_list = [
        QuestionResponse(
            id=q.id,
            question_text=q.question_text,
            options={
                chr(65 + i): option
                for i, option in enumerate(q.options)
            },
            category=q.category
        ) for q in selected_questions
    ]

    return MaterialQuestionsResponse(
        session_id=session_id,
        questions=question_list,
        total_questions=len(question_list)
    )

@router.post(
    "/{material_id}/evaluate-questions",
    response_model=EvaluationResponse
)
async def evaluate_questions(
    material_id: int,
    submission: QuestionAnswerSubmission,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """Evaluate answers using the session to map to correct questions"""
    try:
        # Get session data
        session_data = await question_session_service.get_session(submission.session_id)
        
        # Verify session belongs to correct material and user
        if (session_data["material_id"] != material_id or 
            session_data["user_id"] != current_user.id):
            raise HTTPException(
                status_code=400,
                detail="Invalid session for this material/user"
            )

        # Get all questions for this material
        stmt = select(Question).where(
            Question.material_id == material_id,
            Question.user_id == current_user.id
        )
        result = await db.execute(stmt)
        all_questions = result.scalars().all()

        # Evaluate each answer using session's question order
        results = []
        correct_count = 0
        question_order = session_data["question_order"]

        for answer in submission.answers:
            if answer.question_number < 1 or answer.question_number > len(question_order):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid question number: {answer.question_number}"
                )

            # Get the actual question using stored order
            actual_index = question_order[answer.question_number - 1]
            question = all_questions[actual_index]

            # Convert selected option to answer
            option_index = ord(answer.selected_option.upper()) - ord('A')
            if option_index < 0 or option_index >= len(question.options):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid option '{answer.selected_option}' for question {answer.question_number}"
                )

            selected_answer = question.options[option_index]
            is_correct = selected_answer == question.answer

            if is_correct:
                correct_count += 1

            # Find correct option letter
            correct_option = chr(ord('A') + question.options.index(question.answer))

            results.append(QuestionResult(
                question_number=answer.question_number,
                correct=is_correct,
                selected_option=answer.selected_option,
                correct_option=correct_option if not is_correct else answer.selected_option
            ))

        return EvaluationResponse(
            total_questions=len(submission.answers),
            correct_answers=correct_count,
            score=correct_count / len(submission.answers),
            results=results
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

@router.get(
    "/",
    response_model=MaterialList,
    responses={
        401: {"description": "Not authenticated"}
    }
)
async def get_user_materials(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    source_type: Optional[str] = Query(None, regex="^(pdf|youtube)$"),
    sort_by: str = Query("created_at", regex="^(created_at)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all materials for the current user with optional filtering and sorting.
    
    - **page**: Page number (default: 1)
    - **per_page**: Items per page (default: 20, max: 100)
    - **source_type**: Filter by 'pdf' or 'youtube'
    - **sort_by**: Sort field (currently only 'created_at')
    - **order**: Sort order ('asc' or 'desc')
    """
    # Build query
    query = select(Material).where(Material.owner_id == current_user.id)
    
    # Apply filters
    if source_type:
        query = query.where(Material.source_type == source_type)
    
    # Apply sorting
    if order == "desc":
        query = query.order_by(Material.created_at.desc())
    else:
        query = query.order_by(Material.created_at.asc())
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Apply pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    
    # Execute query
    result = await db.execute(query)
    materials = result.scalars().all()
    
    # Get stats for each material
    material_list = []
    for material in materials:
        # Count flashcards and questions
        flashcards_count = await db.scalar(
            select(func.count()).select_from(Flashcard).where(
                Flashcard.material_id == material.id,
                Flashcard.user_id == current_user.id
            )
        )
        questions_count = await db.scalar(
            select(func.count()).select_from(Question).where(
                Question.material_id == material.id,
                Question.user_id == current_user.id
            )
        )
        
        material_list.append(
            MaterialListItem(
                **material.__dict__,
                stats=MaterialStats(
                    num_flashcards=flashcards_count,
                    num_questions=questions_count
                )
            )
        )
    
    return MaterialList(
        materials=material_list,
        total=total,
        page=page,
        per_page=per_page
    ) 