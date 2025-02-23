# uvicorn app.main:app --reload
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.mongodb import connect_to_mongo, close_mongo_connection
from app.api.v1.api import api_router
from app.api.v1 import jobs, candidates, auth
from app.services.jobs import migrate_job_fields
from app.services.candidates import migrate_candidates_to_gridfs
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
frontend_origins = [
    "https://talent-sourcing-p631.vercel.app",
    "https://your-custom-frontend.vercel.app"
]

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

app.include_router(api_router, prefix=settings.API_V1_STR)

# Add routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["candidates"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        await connect_to_mongo()
        await migrate_job_fields()
        await migrate_candidates_to_gridfs()
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await close_mongo_connection()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 