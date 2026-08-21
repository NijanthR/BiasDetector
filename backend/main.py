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
if cors_env.strip():
    allowed_origins = [o.strip() for o in cors_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

# If wildcard is requested, allow_credentials must be False per CORS spec
is_wildcard = "*" in allowed_origins
allow_origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX", r"https://.*\.vercel\.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=None if is_wildcard else allow_origin_regex,
    allow_credentials=not is_wildcard,
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
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "False").lower() in ("true", "1")
    uvicorn.run("main:app", host=host, port=port, reload=debug)
