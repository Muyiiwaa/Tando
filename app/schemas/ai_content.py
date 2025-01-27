from typing import List, Optional
from pydantic import BaseModel, Field

class Flashcard(BaseModel):
    question: str = Field(..., description="The front side of the flashcard with the question")
    answer: str = Field(..., description="The back side of the flashcard with the answer")
    topic: str = Field(..., description="The main topic this flashcard covers")
    difficulty: str = Field(..., enum=["easy", "medium", "hard"])

class MultipleChoiceQuestion(BaseModel):
    question: str = Field(..., description="The question text")
    choices: List[str] = Field(..., description="List of possible answers", min_items=4, max_items=4)
    correct_index: int = Field(..., description="Index of the correct answer (0-3)", ge=0, le=3)
    explanation: str = Field(..., description="Explanation of why the answer is correct")
    topic: str = Field(..., description="The main topic this question covers")

class AIGenerationRequest(BaseModel):
    text: str = Field(..., description="The text to generate content from")
    num_items: int = Field(default=5, ge=1, le=20, description="Number of items to generate")
    topics: Optional[List[str]] = Field(default=None, description="Specific topics to focus on") 