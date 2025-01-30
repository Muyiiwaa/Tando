from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.progress import Progress
from app.models.material import Material
from app.schemas.progress import ProgressCreate, ProgressUpdate

class ProgressService:
    async def get_progress(
        self,
        db: AsyncSession,
        user_id: int,
        material_id: int
    ) -> Optional[Progress]:
        # First verify material exists and user has access
        material = await self._verify_material_access(db, material_id, user_id)
        
        # Use select statement instead of direct query
        stmt = select(Progress).where(
            Progress.user_id == user_id,
            Progress.material_id == material_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_progress(
        self,
        db: AsyncSession,
        user_id: int,
        material_id: int,
        scores: dict,
        is_flashcard: bool = True
    ) -> Progress:
        # Validate scores
        if not all(0 <= score <= 1 for score in scores.values()):
            raise ValueError("All scores must be between 0 and 1")

        # Verify material exists and user has access
        await self._verify_material_access(db, material_id, user_id)

        progress = await self.get_progress(db, user_id, material_id)
        if not progress:
            progress = Progress(
                user_id=user_id,
                material_id=material_id
            )
            db.add(progress)

        try:
            if is_flashcard:
                progress.flashcard_scores.update(scores)
            else:
                progress.question_scores.update(scores)

            all_scores = list(progress.flashcard_scores.values()) + list(progress.question_scores.values())
            progress.overall_mastery = sum(all_scores) / len(all_scores) if all_scores else 0.0
            progress.last_reviewed = datetime.utcnow()
            progress.next_review = self._calculate_next_review(progress.overall_mastery)
            progress.weak_topics = await self._identify_weak_topics(progress)

            await db.commit()
            await db.refresh(progress)
            return progress
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update progress: {str(e)}"
            )

    def _calculate_next_review(self, mastery: float) -> datetime:
        """
        Implement spaced repetition algorithm
        Lower mastery = more frequent reviews
        """
        base_interval = timedelta(days=1)
        if mastery < 0.3:
            interval = base_interval
        elif mastery < 0.5:
            interval = base_interval * 2
        elif mastery < 0.7:
            interval = base_interval * 4
        elif mastery < 0.9:
            interval = base_interval * 7
        else:
            interval = base_interval * 14

        return datetime.utcnow() + interval

    async def _identify_weak_topics(self, progress: Progress) -> List[str]:
        weak_topics = set()
        threshold = 0.7

        for flashcard_id, score in progress.flashcard_scores.items():
            if score < threshold:
                topic = self._get_topic_for_item(flashcard_id, is_flashcard=True)
                if topic:
                    weak_topics.add(topic)

        for question_id, score in progress.question_scores.items():
            if score < threshold:
                topic = self._get_topic_for_item(question_id, is_flashcard=False)
                if topic:
                    weak_topics.add(topic)

        return list(weak_topics)

    def _get_topic_for_item(self, item_id: str, is_flashcard: bool) -> Optional[str]:
        # Implementation depends on how you store topics for items
        pass 

    async def _verify_material_access(
        self,
        db: AsyncSession,
        material_id: int,
        user_id: int
    ) -> Material:
        stmt = select(Material).where(Material.id == material_id)
        result = await db.execute(stmt)
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Material not found"
            )
        if material.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this material"
            )
        return material
    
