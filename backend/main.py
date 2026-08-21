"""
FastAPI application entrypoint for Dataset Bias & Analysis Platform
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from database import init_db
from routers import datasets, reports, dashboard

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    os.makedirs(os.path.join(UPLOADS_DIR, "datasets"), exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    init_db()
    print("Database tables initialized successfully.")
    yield


# Ensure tables and folders exist immediately upon import
os.makedirs(os.path.join(UPLOADS_DIR, "datasets"), exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
init_db()


app = FastAPI(
    title="Dataset Bias & Quality Analysis API",
    description="High-performance backend API using FastAPI and CrewAI for multi-agent dataset analysis",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
cors_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
allowed_origins = [o.strip() for o in cors_env.split(",") if o.strip()] if cors_env else [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories for file access
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")

# Include API Routers under /api
app.include_router(datasets.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
def root():
    """Root status endpoint"""
    return {
        "status": "online",
        "service": "Dataset Bias & Quality Analysis API",
        "version": "2.0.0",
        "docs_url": "/docs"
    }


@app.get("/api/health/")
@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
