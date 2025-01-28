from typing import List, Optional
from pydantic import BaseModel, Field

class Flashcard(BaseModel):
    id: str = Field(..., description="Unique identifier for the flashcard")
    category: str = Field(..., description="Category of the flashcard")
    front: str = Field(..., description="Front side of the flashcard (question)")
    back: str = Field(..., description="Back side of the flashcard (answer)")
    topic: str = Field(..., description="The main topic this flashcard covers")
    difficulty: str = Field(..., enum=["easy", "medium", "hard"])
    explanation: str = Field(..., description="Additional context or explanation")

class SingleQuestion(BaseModel):
    id: str = Field(..., description="Unique identifier for the question")
    category: str = Field(..., description="Category of the question")
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of 4 answers options for multiple-choice questions")
    answer: str = Field(..., description="The correct answer (string)")
    explanation: str = Field(..., description="Explanation for the answer")

class MultipleQuestions(BaseModel):
    questions: List[SingleQuestion] = Field(..., description="List of questions")

class MultipleFlashcards(BaseModel):
    flashcards: List[Flashcard] = Field(..., description="List of flashcards")

class AIGenerationRequest(BaseModel):
    text: str = Field(..., description="The text to generate content from")
    num_items: int = Field(default=5, ge=1, le=20, description="Number of items to generate")
    topics: Optional[List[str]] = Field(default=None, description="Specific topics to focus on") 