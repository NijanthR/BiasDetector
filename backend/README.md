# Backend - Dataset Bias & Quality Analysis Platform

High-performance, modern Python backend built with **FastAPI**, **SQLAlchemy**, and **CrewAI** for multi-agent dataset analysis, bias detection, and executive reporting.

## 🚀 Features

- **FastAPI Engine**: Ultra-fast asynchronous REST API with automatic OpenAPI documentation.
- **SQLAlchemy ORM**: Flexible database management supporting SQLite & PostgreSQL with WAL concurrency.
- **Multi-Agent Orchestration**: Autonomous agent pipelines powered by CrewAI and LLMs (Groq / Gemini).
- **Comprehensive Quality & Bias Metrics**: Statistical dispersion, class distribution, missing value profiling, text sentiment & keyword extraction.
- **Real-time Agent Logs**: Live execution status tracking across agent tasks.

## 📋 Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## 🛠️ Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```
Ensure your `GROQ_API_KEY` or `GEMINI_API_KEY` is configured.

### 3. Run the Development Server
```bash
uvicorn main:app --reload --port 8000
```
API Documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📂 Project Structure

```
backend/
├── database.py         # SQLAlchemy engine and session dependency
├── models.py           # Database models (Dataset, AnalysisResult, Report, ExecutionLog)
├── schemas.py          # Pydantic request/response schemas
├── main.py             # FastAPI entrypoint, middleware, & router registration
├── requirements.txt    # Python dependencies
├── .env.example        # Example environment configuration
├── routers/            # API Route endpoints
│   ├── datasets.py     # Dataset upload, analysis, history, and results
│   ├── reports.py      # Report retrieval and export
│   └── dashboard.py    # System stats, platform overview, and agent logs
├── crews/              # CrewAI Agents & Orchestration
│   ├── crew_agents.py  # Agent definitions & LLM setup
│   ├── orchestrator.py # Pipeline coordination & execution logging
│   └── tools/          # Statistical & text analysis tools
├── uploads/            # Dataset file storage
└── reports/            # Exported reports storage
```

## 🔌 API Endpoints

### Datasets (`/api/datasets`)
- `POST /api/datasets/upload/` - Upload CSV, XLSX, or JSON dataset.
- `GET /api/datasets/` - List all datasets.
- `GET /api/datasets/{id}/` - Get single dataset details.
- `GET /api/datasets/{id}/details/` - Get dataset with nested analysis results.
- `GET /api/datasets/{id}/results/` - Get agent analysis results.
- `POST /api/datasets/{id}/analyze/` - Trigger analysis.
- `GET /api/datasets/history/` - Get dataset history.
- `DELETE /api/datasets/{id}/` - Delete dataset and associated analyses.

### Reports (`/api/reports`)
- `GET /api/reports/` - List all reports.
- `GET /api/reports/{id}/` - Get report by ID or dataset ID.
- `GET /api/reports/latest_reports/` - Get latest 10 reports.
- `POST /api/reports/{id}/export/` - Export report in JSON.

### Dashboard (`/api/dashboard`)
- `GET /api/dashboard/stats/` - Dashboard counters, recent runs, and active agent execution logs.
- `GET /api/dashboard/overview/` - Platform-wide summary statistics and health averages.
- `GET /api/dashboard/logs/` - Recent 100 execution logs across all datasets.
