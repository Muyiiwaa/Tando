from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_active_user, get_async_db
from app.models.user import User
from app.schemas.progress import Progress, ProgressUpdate
from app.services.progress import ProgressService

router = APIRouter()
progress_service = ProgressService()

@router.get(
    "/{material_id}",
    response_model=Progress,
    responses={
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": {"detail": "No progress found for this material"}
                }
            }
        },
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Not owner of the material"}
    }
)
async def get_progress(
    material_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's progress for a specific material.
    
    - **material_id**: ID of the learning material
    """
    progress = await progress_service.get_progress(
        db,
        current_user.id,
        material_id
    )
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No progress found for this material"
        )
    return progress

@router.post(
    "/flashcard-review",
    response_model=Progress,
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "Invalid scores": {
                            "value": {"detail": "Scores must be between 0 and 1"}
                        },
                        "Missing material": {
                            "value": {"detail": "Material not found"}
                        }
                    }
                }
            }
        }
    }
)
async def update_flashcard_progress(
    material_id: int,
    scores: dict[str, float],
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update flashcard review scores.
    
    - **material_id**: ID of the learning material
    - **scores**: Dictionary mapping flashcard IDs to scores (0-1)
    """
    try:
        return await progress_service.update_progress(
            db,
            current_user.id,
            material_id,
            scores,
            is_flashcard=True
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/question-review", response_model=Progress)
async def update_question_progress(
    material_id: int,
    scores: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    return await progress_service.update_progress(
        db,
        current_user.id,
        material_id,
        scores,
        is_flashcard=False
    )

@router.get("/weak-topics/{material_id}", response_model=List[str])
async def get_weak_topics(
    material_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    progress = await progress_service.get_progress(
        db,
        current_user.id,
        material_id
    )
    if not progress:
        return []
    return progress.weak_topics 