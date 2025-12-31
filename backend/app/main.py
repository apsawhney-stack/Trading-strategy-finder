"""
Strategy Finder Backend - FastAPI Application

A research assistant for options traders that extracts, synthesizes, 
and scores strategy insights from multiple sources.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import extract, strategies, discover
from app.db.database import init_db
from app.middleware.logging import LoggingMiddleware

# Create FastAPI app
app = FastAPI(
    title="Strategy Finder API",
    description="Options strategy research assistant backend",
    version="1.0.0",
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174", 
        "http://localhost:5175",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(extract.router, prefix="/api", tags=["extraction"])
app.include_router(strategies.router, prefix="/api", tags=["strategies"])
app.include_router(discover.router, prefix="/api", tags=["discovery"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
