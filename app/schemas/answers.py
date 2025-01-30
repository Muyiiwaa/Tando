from typing import List, Dict
from pydantic import BaseModel

class QuestionResponse(BaseModel):
    id: str
    question_text: str
    options: Dict[str, str]  # {"A": "option1", "B": "option2", ...}
    category: str

class MaterialQuestionsResponse(BaseModel):
    questions: List[QuestionResponse]
    total_questions: int

class FlashcardDB(BaseModel):
    id: str
    front: str
    back: str

class FlashcardsResponse(BaseModel):
    flashcards: List[FlashcardDB]
    total_returned: int

class QuestionAnswer(BaseModel):
    question_number: int
    selected_option: str  # A, B, C, or D

class QuestionAnswerSubmission(BaseModel):
    answers: List[QuestionAnswer]

class QuestionResult(BaseModel):
    question_number: int
    correct: bool
    selected_option: str
    correct_option: str  # Only included if incorrect

class EvaluationResponse(BaseModel):
    total_questions: int
    correct_answers: int
    score: float  # Percentage correct
    results: List[QuestionResult] 