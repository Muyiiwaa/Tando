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