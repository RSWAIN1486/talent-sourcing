from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.mongodb import connect_to_mongo, close_mongo_connection, ensure_mongo_connection
from app.api.v1.api import api_router
from app.api.v1 import jobs, candidates, auth
from app.services.jobs import migrate_job_fields
from app.services.candidates import migrate_candidates_to_gridfs
import logging
import contextlib

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

frontend_origins = [
    "https://talent-sourcing-p631.vercel.app",
    "https://your-custom-frontend.vercel.app",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://localhost:4173",
    "https://talent-sourcing-fe.onrender.com"
]

# ✅ Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Use FastAPI lifespan to handle startup & shutdown
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """✅ Ensures MongoDB connection is initialized before processing requests."""
    await connect_to_mongo()
    logger.info("✅ MongoDB connection initialized.")

    try:
        await migrate_job_fields()
        await migrate_candidates_to_gridfs()
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}", exc_info=True)
        raise

    yield

    # ✅ Prevent closing MongoDB in Vercel
    logger.info("🔄 Skipping MongoDB shutdown to avoid event loop issues.")

# ✅ Attach the lifespan manager
app.router.lifespan_context = lifespan

# ✅ Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(candidates.router, prefix="/api/v1/candidates", tags=["candidates"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
