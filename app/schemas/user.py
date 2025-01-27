from typing import Optional
from pydantic import BaseModel, EmailStr, constr
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: constr(min_length=8)  # Password must be at least 8 characters

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class UserInDBBase(UserBase):
    id: int
    role: UserRole
    
    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None  # user id 