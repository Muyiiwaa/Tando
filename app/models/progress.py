from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    material_id = Column(Integer, ForeignKey("materials.id"))
    flashcard_scores = Column(JSON, default=dict)  # Store flashcard IDs and their scores
    question_scores = Column(JSON, default=dict)  # Store question IDs and their scores
    overall_mastery = Column(Float, default=0.0)  # 0 to 1.0
    last_reviewed = Column(DateTime, default=datetime.utcnow)
    next_review = Column(DateTime)  # Calculated based on spaced repetition
    weak_topics = Column(JSON, default=list)  # List of topics needing review

    # Relationships
    user = relationship("User", back_populates="progress")
    material = relationship("Material", back_populates="progress") 