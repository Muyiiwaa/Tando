from typing import List, Optional
from openai import OpenAI
from app.core.config import settings
from app.schemas.ai_content import SingleQuestion, MultipleQuestions

class AIGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )

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
        
        return completion.choices[0].message.parsed.questions 