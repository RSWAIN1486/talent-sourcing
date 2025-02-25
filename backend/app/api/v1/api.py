from fastapi import APIRouter
from app.api.v1 import jobs, auth, candidates
from app.api.endpoints import voice_screening

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(voice_screening.router, prefix="/voice-screening", tags=["voice-screening"]) 