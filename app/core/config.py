from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "StudyAI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    SQLITE_URL: str = "sqlite:///./sql_app.db"
    
    # External Services
    SENDGRID_API_KEY: Optional[str] = None
    STRIPE_API_KEY: Optional[str] = None
    GEMINI_API_KEY: str
    
    # OAuth2 configs
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_CLIENT_ID: Optional[str] = None
    FACEBOOK_CLIENT_SECRET: Optional[str] = None

    REDIS_URL: str = "redis://localhost:6379"
    QUESTION_SESSION_TTL: int = 3600  # 1 hour in seconds

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 