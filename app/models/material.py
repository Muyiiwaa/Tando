from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Material(Base):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    source_type = Column(String)  # 'pdf' or 'youtube'
    source_url = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="materials")
    flashcards = relationship("Flashcard", back_populates="material", lazy="dynamic")
    questions = relationship("Question", back_populates="material", lazy="dynamic")
    progress = relationship("Progress", back_populates="material", lazy="dynamic") 