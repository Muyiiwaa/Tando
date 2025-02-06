from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class MaterialBase(BaseModel):
    title: str
    content: str
    source_type: str  # "pdf" or "youtube"
    source_url: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class MaterialResponse(MaterialBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# This is used for internal operations
class MaterialInDB(MaterialResponse):
    pass

class MaterialStats(BaseModel):
    num_flashcards: int
    num_questions: int

class MaterialListItem(MaterialResponse):
    stats: MaterialStats

    class Config:
        from_attributes = True

class MaterialList(BaseModel):
    materials: List[MaterialListItem]
    total: int
    page: int
    per_page: int 