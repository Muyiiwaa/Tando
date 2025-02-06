from typing import List, Optional
from openai import OpenAI
from app.core.config import settings
from app.schemas.ai_content import SingleQuestion, MultipleQuestions, Flashcard, MultipleFlashcards
import openai
from uuid import uuid4

class AIGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

    async def generate_flashcards(
        self,
        text: str,
        num_cards: int = 20,
        topics: Optional[List[str]] = None
    ) -> List[Flashcard]:
        completion = self.client.beta.chat.completions.parse(
            model="gemini-1.5-flash",
            messages=[
                {"role": "system", "content": f"Generate {num_cards} flashcards strictly based on the content given. Do not include any other information and do not go beyond the content."},
                {"role": "user", "content": f"Content: {text}"},
            ],
            response_format=MultipleFlashcards,
        )
        
        # Add unique IDs to each flashcard
        flashcards = completion.choices[0].message.parsed.flashcards
        for card in flashcards:
            card.id = f"fc_{uuid4()}"
        
        return flashcards

    def _parse_ai_response(self, response: str) -> List[dict]:
        """
        Parse the AI response into a list of flashcard dictionaries
        """
        # Implementation depends on the format of the AI response
        # This is a simplified example
        cards = []
        # Parse the response and extract flashcard data
        # Add error handling as needed
        return cards

    async def generate_questions(
        self,
        text: str,
        num_questions: int = 5,
        topics: Optional[List[str]] = None
    ) -> List[SingleQuestion]:
        completion = self.client.beta.chat.completions.parse(
            model="gemini-1.5-flash",
            messages=[
                {"role": "system", "content": f"Generate {num_questions} questions strictly based on the content given. Do not include any other information and do not go beyond the content."},
                {"role": "user", "content": f"Content: {text}"},
            ],
            response_format=MultipleQuestions,
        )
        
        # Add unique IDs to each question
        questions = completion.choices[0].message.parsed.questions
        for question in questions:
            question.id = f"q_{uuid4()}"
        
        return questions