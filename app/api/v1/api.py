from fastapi import APIRouter
from app.api.v1.endpoints import auth, materials, progress

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"]) 