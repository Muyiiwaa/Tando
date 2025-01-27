from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text)
    correct_answer = Column(Text)
    options = Column(JSON)  # List of possible answers
    explanation = Column(Text)
    topic = Column(String, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    material = relationship("Material", back_populates="questions")
    user = relationship("User", back_populates="questions") 