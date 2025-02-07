from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ProgressBase(BaseModel):
    flashcard_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapping of flashcard IDs to mastery scores (0-1)"
    )
    question_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapping of question IDs to scores (0-1)"
    )
    overall_mastery: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall mastery level"
    )
    weak_topics: List[str] = Field(
        default_factory=list,
        description="Topics that need more review"
    )

class ProgressCreate(ProgressBase):
    material_id: int

class ProgressUpdate(ProgressBase):
    pass

class Progress(ProgressBase):
    id: int
    user_id: int
    material_id: int
    last_reviewed: datetime
    next_review: datetime

    class Config:
        from_attributes = True

class ProgressStats(BaseModel):
    """Detailed statistics for a material's progress"""
    total_questions: int
    questions_attempted: int
    total_flashcards: int
    flashcards_reviewed: int
    overall_mastery: float = Field(ge=0.0, le=1.0)
    last_reviewed: Optional[datetime]
    next_review: Optional[datetime]
    average_question_score: float = Field(ge=0.0, le=1.0)
    average_flashcard_score: float = Field(ge=0.0, le=1.0)

class CategoryProgress(BaseModel):
    """Progress for a specific question category"""
    category: str
    total_questions: int
    correct_answers: int
    mastery_level: float = Field(ge=0.0, le=1.0)

class WeakAreasResponse(BaseModel):
    """Analysis of weak areas in the material"""
    weak_categories: List[CategoryProgress]
    recommended_focus: List[str]
    lowest_scoring_questions: List[str]
    overall_weak_areas_count: int

class MaterialProgress(BaseModel):
    """Progress summary for a single material"""
    material_id: int
    title: str
    overall_mastery: float = Field(ge=0.0, le=1.0)
    last_reviewed: Optional[datetime]
    questions_completed: int
    flashcards_reviewed: int
    weak_areas_count: int

class MaterialProgressList(BaseModel):
    """Paginated list of material progress"""
    materials: List[MaterialProgress]
    total: int
    page: int
    per_page: int

class ReviewResponse(BaseModel):
    """Response model for review updates"""
    material_id: int
    flashcard_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapping of flashcard IDs to scores (0-1)"
    )
    question_scores: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapping of question IDs to scores (0-1)"
    )
    overall_mastery: float = Field(
        ge=0.0,
        le=1.0,
        description="Overall mastery level"
    )
    last_reviewed: datetime
    next_review: datetime

    class Config:
        from_attributes = True 