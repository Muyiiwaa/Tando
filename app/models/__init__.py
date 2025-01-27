from app.models.base import Base
from app.models.user import User
from app.models.material import Material
from app.models.flashcard import Flashcard
from app.models.question import Question
from app.models.progress import Progress

# This ensures all models are registered with SQLAlchemy
__all__ = ["Base", "User", "Material", "Flashcard", "Question", "Progress"] 