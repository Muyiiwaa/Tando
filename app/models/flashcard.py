from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, index=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    material_id = Column(Integer, ForeignKey("materials.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    material = relationship("Material", back_populates="flashcards")
    user = relationship("User", back_populates="flashcards") 