from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.dependencies import get_current_active_user, get_async_db
from app.models.user import User
from app.models.material import Material
from app.models.question import Question
from app.models.flashcard import Flashcard
from app.models.progress import Progress
from app.schemas.progress import (
    ProgressStats,
    WeakAreasResponse,
    MaterialProgress,
    MaterialProgressList,
    ReviewResponse
)
from app.services.progress import ProgressService

router = APIRouter()
progress_service = ProgressService()

@router.get(
    "/{material_id}/stats",
    response_model=ProgressStats,
    responses={404: {"description": "Material not found"}}
)
async def get_material_progress_stats(
    material_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed progress statistics for a specific material
    """
    return await progress_service.get_material_stats(
        db,
        material_id,
        current_user.id
    )

@router.get(
    "/materials",
    response_model=MaterialProgressList
)
async def get_materials_progress(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get progress overview for all materials
    """
    return await progress_service.get_all_materials_progress(
        db,
        current_user.id,
        page,
        per_page
    )

@router.post(
    "/{material_id}/update-session",
    response_model=ProgressStats,
    responses={404: {"description": "Material not found"}}
)
async def update_study_session(
    material_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update progress after a study session
    """
    return await progress_service.update_study_session(
        db,
        material_id,
        current_user.id
    )

@router.get(
    "/{material_id}/weak-areas",
    response_model=WeakAreasResponse,
    responses={404: {"description": "Material not found"}}
)
async def get_weak_areas(
    material_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get analysis of weak areas based on question categories
    """
    return await progress_service.get_weak_areas(
        db,
        material_id,
        current_user.id
    )

@router.post(
    "/flashcard-review",
    response_model=ReviewResponse,
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

@router.post(
    "/question-review",
    response_model=ReviewResponse
)
async def update_question_progress(
    material_id: int,
    scores: dict,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update question review scores.
    
    - **material_id**: ID of the learning material
    - **scores**: Dictionary mapping question IDs to scores (0-1)
    """
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