
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.database import router as database_router
from app.core.config import settings

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
