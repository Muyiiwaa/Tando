from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core import security
from app.core.config import settings
from app.core.dependencies import get_async_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate, UserResponse, Token
from app.services.auth import authenticate_user, create_user

router = APIRouter()

@router.post(
    "/login",
    response_model=Token,
    responses={
        401: {"description": "Unauthorized"}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    """
    OAuth2 compatible token login.
    
    - **username**: Email address
    - **password**: User password
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "Email exists": {
                            "value": {"detail": "Email already registered"}
                        },
                        "Invalid email": {
                            "value": {"detail": "Invalid email format"}
                        }
                    }
                }
            }
        }
    }
)
async def signup(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new user account.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: User's full name
    """
    try:
        user = await create_user(db, user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 