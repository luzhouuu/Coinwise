"""FastAPI application entry point.

This module initializes the FastAPI application with all routers and middleware.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import SessionLocal, init_db, init_default_categories
from app.routers import analysis, auth, budgets, chat, config, statistics, sync, transactions
from app.services.scheduler import init_scheduler, shutdown_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Initialize database on startup
    init_db()
    # Initialize default categories
    db = SessionLocal()
    try:
        init_default_categories(db)
    finally:
        db.close()
    # Start scheduler for automated sync
    init_scheduler()
    yield
    # Shutdown scheduler on exit
    shutdown_scheduler()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
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
app.include_router(
    transactions.router,
    prefix=f"{settings.api_prefix}/transactions",
    tags=["transactions"],
)
app.include_router(
    sync.router,
    prefix=f"{settings.api_prefix}/sync",
    tags=["sync"],
)
app.include_router(
    config.router,
    prefix=f"{settings.api_prefix}/config",
    tags=["config"],
)
app.include_router(
    statistics.router,
    prefix=f"{settings.api_prefix}/statistics",
    tags=["statistics"],
)
app.include_router(
    budgets.router,
    prefix=f"{settings.api_prefix}/budgets",
    tags=["budgets"],
)
app.include_router(
    analysis.router,
    prefix=f"{settings.api_prefix}",
    tags=["analysis"],
)
app.include_router(
    auth.router,
    prefix=f"{settings.api_prefix}/auth",
    tags=["auth"],
)
app.include_router(
    chat.router,
    prefix=f"{settings.api_prefix}",
    tags=["chat"],
)


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": f"{settings.api_prefix}/docs",
    }


@app.get(f"{settings.api_prefix}/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
