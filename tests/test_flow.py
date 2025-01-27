import asyncio
import httpx
import pytest
from typing import Dict

BASE_URL = "http://localhost:8086/api/v1"

async def test_full_flow():
    async with httpx.AsyncClient() as client:
        # 1. Sign up
        signup_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = await client.post(f"{BASE_URL}/auth/signup", json=signup_data)
        assert response.status_code == 200
        user_data = response.json()
        
        # 2. Login
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        response = await client.post(f"{BASE_URL}/auth/login", data=login_data)
        assert response.status_code == 200
        token_data = response.json()
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        
        # 3. Upload a YouTube video transcript
        upload_data = {
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "title": "Test Material"
        }
        response = await client.post(
            f"{BASE_URL}/materials/upload/youtube",
            data=upload_data,
            headers=headers
        )
        assert response.status_code == 200
        material_data = response.json()
        material_id = material_data["id"]
        
        # 4. Generate flashcards
        response = await client.post(
            f"{BASE_URL}/materials/{material_id}/generate-flashcards",
            params={"num_cards": 3},
            headers=headers
        )
        assert response.status_code == 200
        flashcards = response.json()
        assert len(flashcards) == 3
        
        # 5. Generate questions
        response = await client.post(
            f"{BASE_URL}/materials/{material_id}/generate-questions",
            params={"num_questions": 3},
            headers=headers
        )
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) == 3
        
        # 6. Update flashcard progress
        flashcard_scores = {
            str(flashcards[0]["id"]): 0.8,
            str(flashcards[1]["id"]): 0.6,
            str(flashcards[2]["id"]): 0.9
        }
        response = await client.post(
            f"{BASE_URL}/progress/flashcard-review",
            params={"material_id": material_id},
            json=flashcard_scores,
            headers=headers
        )
        assert response.status_code == 200
        
        # 7. Get progress
        response = await client.get(
            f"{BASE_URL}/progress/{material_id}",
            headers=headers
        )
        assert response.status_code == 200
        progress_data = response.json()
        assert progress_data["overall_mastery"] > 0
        
        # 8. Get weak topics
        response = await client.get(
            f"{BASE_URL}/progress/weak-topics/{material_id}",
            headers=headers
        )
        assert response.status_code == 200
        weak_topics = response.json()
        assert isinstance(weak_topics, list)

if __name__ == "__main__":
    asyncio.run(test_full_flow()) 