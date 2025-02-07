from datetime import datetime, timedelta
from typing import List, Optional, Dict
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.progress import Progress
from app.models.material import Material
from app.models.question import Question
from app.models.flashcard import Flashcard
from app.schemas.progress import (
    ProgressStats, CategoryProgress, WeakAreasResponse,
    MaterialProgress, MaterialProgressList
)

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

    async def get_material_stats(
        self,
        db: AsyncSession,
        material_id: int,
        user_id: int
    ) -> ProgressStats:
        # Verify material access
        material = await self._verify_material_access(db, material_id, user_id)
        
        # Get progress record
        progress = await self._get_or_create_progress(db, material_id, user_id)
        
        # Get question stats
        questions_query = select(func.count(Question.id)).where(
            Question.material_id == material_id,
            Question.user_id == user_id
        )
        total_questions = await db.scalar(questions_query)
        
        # Get flashcard stats
        flashcards_query = select(func.count(Flashcard.id)).where(
            Flashcard.material_id == material_id,
            Flashcard.user_id == user_id
        )
        total_flashcards = await db.scalar(flashcards_query)
        
        return ProgressStats(
            total_questions=total_questions,
            questions_attempted=len(progress.question_scores),
            total_flashcards=total_flashcards,
            flashcards_reviewed=len(progress.flashcard_scores),
            overall_mastery=progress.overall_mastery,
            last_reviewed=progress.last_reviewed,
            next_review=progress.next_review,
            average_question_score=self._calculate_average(progress.question_scores),
            average_flashcard_score=self._calculate_average(progress.flashcard_scores)
        )

    async def get_weak_areas(
        self,
        db: AsyncSession,
        material_id: int,
        user_id: int
    ) -> WeakAreasResponse:
        # Verify material access
        await self._verify_material_access(db, material_id, user_id)
        
        # Get questions with categories
        stmt = select(Question).where(
            Question.material_id == material_id,
            Question.user_id == user_id
        )
        result = await db.execute(stmt)
        questions = result.scalars().all()
        
        # Get progress
        progress = await self._get_or_create_progress(db, material_id, user_id)
        
        # Calculate category progress
        category_stats = {}
        for question in questions:
            if question.category not in category_stats:
                category_stats[question.category] = {
                    "total": 0,
                    "correct": 0,
                    "score": 0.0
                }
            
            stats = category_stats[question.category]
            stats["total"] += 1
            
            if question.id in progress.question_scores:
                score = progress.question_scores[question.id]
                stats["score"] += score
                if score > 0.7:  # Consider correct if score > 70%
                    stats["correct"] += 1
        
        # Create category progress list
        categories = [
            CategoryProgress(
                category=cat,
                total_questions=stats["total"],
                correct_answers=stats["correct"],
                mastery_level=stats["score"] / stats["total"] if stats["total"] > 0 else 0.0
            )
            for cat, stats in category_stats.items()
        ]
        
        # Sort by mastery level to find weak areas
        weak_categories = sorted(categories, key=lambda x: x.mastery_level)
        
        return WeakAreasResponse(
            weak_categories=weak_categories,
            recommended_focus=[cat.category for cat in weak_categories[:3]],
            lowest_scoring_questions=self._get_lowest_scoring_questions(progress.question_scores, 5),
            overall_weak_areas_count=len([c for c in weak_categories if c.mastery_level < 0.7])
        )

    def _calculate_average(self, scores: Dict[str, float]) -> float:
        if not scores:
            return 0.0
        return sum(scores.values()) / len(scores)

    async def _get_or_create_progress(
        self,
        db: AsyncSession,
        material_id: int,
        user_id: int
    ) -> Progress:
        progress = await self.get_progress(db, user_id, material_id)
        if not progress:
            progress = Progress(
                user_id=user_id,
                material_id=material_id,
                flashcard_scores={},
                question_scores={},
                overall_mastery=0.0,
                last_reviewed=datetime.utcnow(),
                next_review=datetime.utcnow()
            )
            db.add(progress)
            await db.commit()
            await db.refresh(progress)
        return progress

    def _get_lowest_scoring_questions(
        self,
        question_scores: Dict[str, float],
        limit: int
    ) -> List[str]:
        sorted_questions = sorted(
            question_scores.items(),
            key=lambda x: x[1]
        )
        return [q[0] for q in sorted_questions[:limit]]

    async def get_all_materials_progress(
        self,
        db: AsyncSession,
        user_id: int,
        page: int,
        per_page: int
    ) -> MaterialProgressList:
        """Get paginated progress for all materials owned by user"""
        # Get base query for user's materials
        base_query = select(Material).where(Material.owner_id == user_id)
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total = await db.scalar(count_query)
        
        # Apply pagination
        query = base_query.offset((page - 1) * per_page).limit(per_page)
        result = await db.execute(query)
        materials = result.scalars().all()
        
        # Get progress for each material
        material_progress = []
        for material in materials:
            # Get progress record
            progress = await self._get_or_create_progress(db, material.id, user_id)
            
            # Count questions and flashcards
            questions_query = select(func.count(Question.id)).where(
                Question.material_id == material.id,
                Question.user_id == user_id
            )
            questions_completed = await db.scalar(questions_query)
            
            flashcards_query = select(func.count(Flashcard.id)).where(
                Flashcard.material_id == material.id,
                Flashcard.user_id == user_id
            )
            flashcards_reviewed = await db.scalar(flashcards_query)
            
            # Count weak areas (categories with mastery < 0.7)
            weak_areas = len([
                cat for cat in set(q.category for q in material.questions)
                if self._calculate_category_mastery(
                    progress.question_scores,
                    [q for q in material.questions if q.category == cat]
                ) < 0.7
            ])
            
            material_progress.append(MaterialProgress(
                material_id=material.id,
                title=material.title,
                overall_mastery=progress.overall_mastery,
                last_reviewed=progress.last_reviewed,
                questions_completed=len(progress.question_scores),
                flashcards_reviewed=len(progress.flashcard_scores),
                weak_areas_count=weak_areas
            ))
        
        return MaterialProgressList(
            materials=material_progress,
            total=total,
            page=page,
            per_page=per_page
        )

    async def update_study_session(
        self,
        db: AsyncSession,
        material_id: int,
        user_id: int
    ) -> ProgressStats:
        """Update progress after a study session"""
        # Verify material access
        material = await self._verify_material_access(db, material_id, user_id)
        
        # Get progress record
        progress = await self._get_or_create_progress(db, material_id, user_id)
        
        # Update last reviewed time
        progress.last_reviewed = datetime.utcnow()
        
        # Recalculate overall mastery
        all_scores = list(progress.flashcard_scores.values()) + list(progress.question_scores.values())
        if all_scores:
            progress.overall_mastery = sum(all_scores) / len(all_scores)
        
        # Calculate next review based on mastery
        progress.next_review = self._calculate_next_review(progress.overall_mastery)
        
        # Update weak topics
        progress.weak_topics = await self._identify_weak_topics(progress)
        
        # Save changes
        await db.commit()
        await db.refresh(progress)
        
        # Return updated stats
        return await self.get_material_stats(db, material_id, user_id)

    def _calculate_category_mastery(
        self,
        question_scores: Dict[str, float],
        category_questions: List[Question]
    ) -> float:
        """Calculate mastery level for a specific category"""
        if not category_questions:
            return 0.0
        
        scores = [
            question_scores.get(q.id, 0.0)
            for q in category_questions
        ]
        return sum(scores) / len(category_questions)
    
