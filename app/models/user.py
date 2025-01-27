from typing import List
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.models.base import Base

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)

    # Relationships
    materials = relationship("Material", back_populates="owner", lazy="dynamic")
    progress = relationship("Progress", back_populates="user", lazy="dynamic")
    flashcards = relationship("Flashcard", back_populates="user", lazy="dynamic")
    questions = relationship("Question", back_populates="user", lazy="dynamic") 