# Complete Setup Guide - Multi-Agent Dataset Analysis Platform

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Backend Setup](#backend-setup)
3. [Frontend Setup](#frontend-setup)
4. [Running Both Services](#running-both-services)
5. [Database Setup](#database-setup)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Hardware
- **Processor:** Intel i5 or equivalent (quad-core minimum)
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 2GB free space
- **Network:** Internet connection for LLM APIs and dependency downloads

### Software
- **Python:** 3.10 or higher
- **Node.js:** 18.0.0 or higher
- **npm:** 8.0.0 or higher
- **Database:** SQLite (default) or PostgreSQL (optional)

---

## Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create `.env` file in the `backend/` directory:
```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key

DATABASE_URL=sqlite:///./db.sqlite3
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173
```

### Step 5: Start the Backend Server

```bash
uvicorn main:app --reload --port 8000
```

✅ **Backend is running at `http://localhost:8000`**
- Interactive API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Start Development Server

```bash
npm run dev
```

✅ **Frontend is running at `http://localhost:5173`**

---

## Running Both Services

### Terminal 1: Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

---

## Testing

Run the test suite:
```bash
cd backend
python test_crew.py
```
