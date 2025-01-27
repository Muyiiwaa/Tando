import os
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

class SingleQuestion(BaseModel):
    id: str = Field(..., description="Unique identifier for the question")
    category: str = Field(..., description="Category of the question")
    question: str = Field(..., description="The question text")
    options: List[str] = Field(..., description="List of 4 answers options for multiple-choice questions")
    answer: str = Field(..., description="The correct answer (string)")
    explanation: str = Field(..., description="Explanation for the answer")




class MultipleQuestions(BaseModel):
    questions: List[SingleQuestion] = Field(..., description="List of questions")

def generate_questions(content: str, num_questions: int) -> MultipleQuestions:
    completion = client.beta.chat.completions.parse(
        model="gemini-1.5-flash",
        messages=[
            {"role": "system", "content": f"Generate {num_questions} questions strictly based on the content given. Do not include any other information and do not go beyond the content."},
            {"role": "user", "content": f"Content: {content}"},
        ],
        response_format=MultipleQuestions,)
    
    return completion.choices[0].message.parsed

if __name__ == "__main__":
    content = input("Enter the content: ")
    num_questions = int(input("Enter the number of questions: "))
    questions = generate_questions(content, num_questions)
    print(questions)