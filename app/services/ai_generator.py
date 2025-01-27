from typing import List, Optional
import google.generativeai as genai
import json
from app.core.config import settings
from app.schemas.ai_content import Flashcard, MultipleChoiceQuestion

class AIGenerator:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_flashcards(
        self,
        text: str,
        num_cards: int = 5,
        topics: Optional[List[str]] = None
    ) -> List[Flashcard]:
        prompt = self._create_flashcard_prompt(text, num_cards, topics)
        
        # Create a structured prompt for Gemini
        structured_prompt = f"""
        {prompt}
        
        Return the flashcards in the following JSON format:
        {{
            "flashcards": [
                {{
                    "question": "question text",
                    "answer": "answer text",
                    "topic": "topic name",
                    "difficulty": "easy|medium|hard"
                }}
            ]
        }}
        Only return the JSON, no other text.
        """

        response = await self.model.generate_content_async(structured_prompt)
        try:
            # Parse the response text as JSON
            response_json = json.loads(response.text)
            # Convert the dictionary items to Flashcard objects
            flashcards = [Flashcard(**card) for card in response_json["flashcards"]]
            return flashcards
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {str(e)}")

    async def generate_questions(
        self,
        text: str,
        num_questions: int = 5,
        topics: Optional[List[str]] = None
    ) -> List[MultipleChoiceQuestion]:
        prompt = self._create_question_prompt(text, num_questions, topics)
        
        structured_prompt = f"""
        {prompt}
        
        Return the questions in the following JSON format:
        {{
            "questions": [
                {{
                    "question": "question text",
                    "choices": ["choice1", "choice2", "choice3", "choice4"],
                    "correct_index": 0,
                    "explanation": "explanation text",
                    "topic": "topic name"
                }}
            ]
        }}
        Only return the JSON, no other text.
        """

        response = await self.model.generate_content_async(structured_prompt)
        try:
            response_json = json.loads(response.text)
            questions = [MultipleChoiceQuestion(**q) for q in response_json["questions"]]
            return questions
        except Exception as e:
            raise ValueError(f"Failed to parse Gemini response: {str(e)}")

    def _create_flashcard_prompt(
        self,
        text: str,
        num_cards: int,
        topics: Optional[List[str]]
    ) -> str:
        base_prompt = f"Create {num_cards} study flashcards from the following text. "
        if topics:
            base_prompt += f"Focus on these topics: {', '.join(topics)}. "
        return base_prompt + f"Text: {text}"

    def _create_question_prompt(
        self,
        text: str,
        num_questions: int,
        topics: Optional[List[str]]
    ) -> str:
        base_prompt = f"Create {num_questions} multiple-choice questions from the following text. "
        if topics:
            base_prompt += f"Focus on these topics: {', '.join(topics)}. "
        return base_prompt + f"Text: {text}" 