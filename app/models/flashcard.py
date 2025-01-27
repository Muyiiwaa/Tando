from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    front = Column(Text)
    back = Column(Text)
    topic = Column(String, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    material = relationship("Material", back_populates="flashcards")
    user = relationship("User", back_populates="flashcards") 