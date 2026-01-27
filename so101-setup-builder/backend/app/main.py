from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.endpoints import (
    wizard,
    components,
    recommendations,
    pricing,
    comparison,
    export,
    docs,
)
from app.db.database import engine, Base

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="API for configuring SO-101 robot arm setups with intelligent recommendations",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(wizard.router, prefix="/api/v1/wizard", tags=["Wizard"])
app.include_router(components.router, prefix="/api/v1/components", tags=["Components"])
app.include_router(
    recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"]
)
app.include_router(pricing.router, prefix="/api/v1/pricing", tags=["Pricing"])
app.include_router(comparison.router, prefix="/api/v1/comparison", tags=["Comparison"])
app.include_router(export.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(docs.router, prefix="/api/v1/docs", tags=["Documentation"])


@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
