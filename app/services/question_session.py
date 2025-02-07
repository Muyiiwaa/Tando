from uuid import uuid4
from typing import List
import json
import redis.asyncio as redis
from app.core.config import settings

class QuestionSessionService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)
        self.ttl = settings.QUESTION_SESSION_TTL

    async def create_session(
        self,
        material_id: int,
        user_id: int,
        question_order: List[int]
    ) -> str:
        session_id = f"qsess_{uuid4()}"
        session_data = {
            "material_id": material_id,
            "user_id": user_id,
            "question_order": question_order
        }
        
        await self.redis.setex(
            session_id,
            self.ttl,
            json.dumps(session_data)
        )
        return session_id

    async def get_session(self, session_id: str) -> dict:
        data = await self.redis.get(session_id)
        if not data:
            raise ValueError("Question session expired or not found")
        return json.loads(data) 