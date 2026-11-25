
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.database import router as database_router
from app.core.config import settings
from app.api.routes.profile import router as profile_router
from app.api.routes.job_preferences import router as job_preferences_router
from app.api.routes.resumes import router as resumes_router

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered job discovery, matching, and career management platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Welcome to AI Career Agent API",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
    }


app.include_router(
    health_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Health"],
)

app.include_router(
    database_router,
    prefix=settings.API_V1_PREFIX,
    tags=["Database"],
)
app.include_router(
    auth_router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["Authentication"],
)
app.include_router(
    profile_router,
    prefix=f"{settings.API_V1_PREFIX}/profile",
    tags=["Candidate Profile"],
)
app.include_router(
    job_preferences_router,
    prefix=f"{settings.API_V1_PREFIX}/job-preferences",
    tags=["Job Preferences"],
)

app.include_router(
    resumes_router,
    prefix=f"{settings.API_V1_PREFIX}/resumes",
    tags=["Resumes"],
)