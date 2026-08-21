# Docker Deployment Guide - Multi-Agent Dataset Analysis Platform

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (Docker Compose)](#quick-start-docker-compose)
3. [Individual Docker Builds](#individual-docker-builds)
4. [Environment Configuration](#environment-configuration)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Docker:** 20.10.0 or higher
- **Docker Compose:** 2.0.0 or higher
- **RAM:** Minimum 8GB (16GB recommended)
- **Disk Space:** 10GB free space

---

## Quick Start (Docker Compose)

### Step 1: Start All Services

```bash
# Build and start services in background
docker-compose up -d --build
```

### Step 2: Access Applications

- **Frontend:** `http://localhost:5173`
- **Backend API Docs:** `http://localhost:8000/docs`
- **Backend ReDoc:** `http://localhost:8000/redoc`

### Step 3: View Logs

```bash
docker-compose logs -f backend
```

### Step 4: Stop Services

```bash
docker-compose down
```

---

## Individual Docker Builds

### Backend Only

**Build:**
```bash
cd backend
docker build -t dataset-platform-backend:latest .
```

**Run:**
```bash
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e GROQ_API_KEY=your_key \
  -e GEMINI_API_KEY=your_key \
  dataset-platform-backend:latest
```

### Frontend Only

**Build:**
```bash
cd frontend
docker build -t dataset-platform-frontend:latest .
```

**Run:**
```bash
docker run -p 5173:5173 dataset-platform-frontend:latest
```

---

## Environment Configuration

Make sure your API keys are provided via environment variables or a `.env` file mounted into the containers.
