from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, index=True)
    category = Column(String, index=True)
    question_text = Column(Text)
    options = Column(JSON)  # List of possible answers
    answer = Column(Text)
    explanation = Column(Text)
    material_id = Column(Integer, ForeignKey("materials.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    material = relationship("Material", back_populates="questions")
    user = relationship("User", back_populates="questions") 