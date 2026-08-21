# Multi-Agent Intelligent Dataset Analysis and Bias Detection Platform

A full-stack AI-powered dataset analysis platform that accepts datasets and automatically analyzes quality, bias, structure, statistics, and recommendations using multiple CrewAI agents running in parallel.

## 🎯 Features

### Analysis Capabilities
- **Dataset Classification** - Automatically detect dataset type (numerical, categorical, time-series, sentiment, transaction, mixed)
- **Quality Assessment** - Missing values, duplicates, consistency checks, completeness scoring
- **Bias Detection** - Class imbalance analysis, entropy calculation, fairness reporting
- **Numerical Analysis** - Descriptive statistics, correlation analysis, outlier detection
- **Categorical Analysis** - Frequency analysis, cardinality, chi-square tests
- **Sentiment Analysis** - Text sentiment classification, keyword extraction
- **Time Series Analysis** - Trend detection, seasonality analysis, anomaly detection, forecast readiness
- **Transaction Analysis** - Fraud indicators, revenue analysis, customer segmentation
- **Mixed Data Analysis** - Cross-feature relationships, encoding suggestions
- **Recommendations** - Data cleaning, preprocessing, model recommendations
- **Report Generation** - Comprehensive PDF/JSON/HTML reports

### Supported Data Types
- CSV files
- XLSX (Excel) files
- JSON files
- Maximum file size: 100 MB

### Data Structures Supported
1. **Numerical Data** - Financial data, measurements, continuous variables
2. **Categorical Data** - Categories, tags, classifications
3. **Time Series Data** - Temporal sequences, trends, seasonality
4. **Sentiment/Text Data** - Reviews, comments, sentiment analysis
5. **Transaction Data** - Orders, purchases, financial transactions
6. **Mixed Data** - Combinations of the above

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI 0.110+
- Uvicorn - ASGI server
- SQLAlchemy 2.0+ - ORM & Database Layer
- CrewAI - Multi-agent orchestration
- Pandas - Data manipulation
- Scikit-learn - Machine learning
- NumPy - Numerical computing
- Plotly - Visualizations

**Frontend:**
- React 19
- React Router DOM - Navigation
- Axios - API communication
- Chart.js - Charts
- TailwindCSS - Styling

**Database:**
- SQLite (default development)
- PostgreSQL (production-ready)

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                           │
│  (Dashboard, Upload, Report Viewer, History)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                  REST APIs (JSON)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   FastAPI Backend                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Agent Orchestrator                           │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │  Parallel Agent Execution                       │ │  │
│  │  │  ├─ Dataset Classifier Agent                    │ │  │
│  │  │  ├─ Quality Agent                               │ │  │
│  │  │  ├─ Bias Detection Agent                        │ │  │
│  │  │  ├─ Numerical Agent                             │ │  │
│  │  │  ├─ Categorical Agent                           │ │  │
│  │  │  ├─ Sentiment Agent                             │ │  │
│  │  │  ├─ Time Series Agent                           │ │  │
│  │  │  ├─ Transaction Agent                           │ │  │
│  │  │  ├─ Mixed Data Agent                            │ │  │
│  │  │  ├─ Recommendation Agent                        │ │  │
│  │  │  ├─ Cleaning Agent                              │ │  │
│  │  │  └─ Report Agent                                │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                      │                                      │
│  ┌──────────────────▼──────────────────────────────────┐  │
│  │     SQLAlchemy Models                               │  │
│  │  ├─ Dataset                                         │  │
│  │  ├─ AnalysisResult                                 │  │
│  │  ├─ Report                                         │  │
│  │  └─ ExecutionLog                                   │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
├── backend/
│   ├── main.py               # FastAPI application entrypoint
│   ├── database.py           # SQLAlchemy configuration & sessions
│   ├── models.py             # Database models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── requirements.txt      # Python dependencies
│   ├── routers/              # API Route endpoints
│   │   ├── datasets.py
│   │   ├── reports.py
│   │   └── dashboard.py
│   ├── crews/                # CrewAI Agents & Orchestrator
│   │   ├── agents/
│   │   ├── tools/
│   │   └── orchestrator.py
│   ├── uploads/
│   ├── reports/
│   └── db.sqlite3
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── src/
    │   ├── App.jsx
    │   ├── pages/
    │   ├── components/
    │   └── services/api.js
    └── public/
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip and npm

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run development server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

The backend will run on `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`)

The backend will run on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

The frontend will run on `http://localhost:5173`

## 📖 API Documentation

### Endpoints

#### Datasets
- `POST /api/datasets/upload/` - Upload new dataset
- `GET /api/datasets/` - List all datasets
- `GET /api/datasets/{id}/` - Get dataset details
- `GET /api/datasets/{id}/results/` - Get analysis results
- `POST /api/datasets/{id}/analyze/` - Trigger analysis
- `GET /api/datasets/history/` - Get upload history
- `DELETE /api/datasets/{id}/` - Delete dataset

#### Reports
- `GET /api/reports/` - List all reports
- `GET /api/reports/{id}/` - Get specific report
- `GET /api/reports/latest/` - Get latest reports
- `POST /api/reports/{id}/export/` - Export report

#### Dashboard
- `GET /api/dashboard/stats/` - Dashboard statistics
- `GET /api/dashboard/overview/` - Platform overview

## 🧠 Agent Descriptions

### 1. Dataset Classifier Agent
Analyzes and classifies the dataset type and structure.

**Input:** DataFrame
**Output:**
- Dataset type (numerical/categorical/time-series/sentiment/transaction/mixed)
- Column type information
- Schema details

### 2. Quality Agent
Assesses data quality metrics and identifies issues.

**Input:** DataFrame
**Output:**
- Quality score (0-100)
- Missing values percentage
- Duplicate records count
- Completeness metrics
- Problem areas identified

### 3. Bias Detection Agent
Detects class imbalance and bias in datasets.

**Input:** DataFrame
**Output:**
- Overall bias score
- Per-column bias metrics
- Entropy calculations
- Fairness report
- Recommendations for rebalancing

### 4. Numerical Agent
Analyzes numerical features in detail.

**Input:** DataFrame, Numeric columns
**Output:**
- Descriptive statistics
- Correlation matrix
- Outlier detection
- Distribution analysis
- Visualization data

### 5. Categorical Agent
Analyzes categorical features.

**Input:** DataFrame, Categorical columns
**Output:**
- Frequency distributions
- Cardinality analysis
- Imbalance ratios
- Visualization data

### 6. Sentiment Agent
Analyzes text and sentiment data.

**Input:** DataFrame, Text columns
**Output:**
- Sentiment distribution
- Polarity and subjectivity scores
- Keyword extraction
- Topic analysis

### 7. Time Series Agent
Analyzes temporal data.

**Input:** DataFrame, Datetime columns
**Output:**
- Trend analysis
- Seasonality detection
- Anomaly detection
- Stationarity tests
- Forecast readiness score

### 8. Transaction Agent
Analyzes transaction and financial data.

**Input:** DataFrame
**Output:**
- Transaction summary
- Fraud indicators
- Revenue trends
- Customer segmentation

### 9. Mixed Data Agent
Analyzes relationships across data types.

**Input:** DataFrame
**Output:**
- Feature interactions
- Encoding suggestions
- Feature importance scores

### 10. Recommendation Agent
Generates improvement recommendations.

**Input:** DataFrame, Analysis results
**Output:**
- Data cleaning suggestions
- Preprocessing recommendations
- Model recommendations
- Improvement suggestions
- Prioritized action items

### 11. Cleaning Agent
Suggests specific cleaning operations.

**Input:** DataFrame
**Output:**
- Missing value handling strategies
- Duplicate removal recommendations
- Outlier handling suggestions
- Data type issue fixes
- Standardization suggestions

### 12. Report Agent
Generates comprehensive analysis reports.

**Input:** DataFrame, All analysis results
**Output:**
- Executive summary
- Dataset overview
- Key findings
- Recommendations summary
- Conclusion

## 🛠️ Configuration

### Backend Configuration

Edit `backend/.env`:

```bash
# Environment Configuration (.env)
DATABASE_URL=sqlite:///./db.sqlite3
# For PostgreSQL in production:
# DATABASE_URL=postgresql://user:password@localhost:5432/dataset_platform

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Configuration

Edit `frontend/src/services/api.js`:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

## 🐳 Docker Deployment

### Build Backend Container

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t dataset-platform-backend .
docker run -p 8000:8000 dataset-platform-backend
```

### Build Frontend Container

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json .
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["npm", "run", "preview"]
```

## 📊 Example Workflow

1. **Upload Dataset**
   - User uploads CSV/XLSX/JSON file
   - File is validated and stored

2. **Automatic Analysis**
   - Classifier determines dataset type
   - Core agents run in parallel (Quality, Bias, Recommendations, Cleaning)
   - Type-specific agents run based on classification
   - All results aggregated

3. **Report Generation**
   - Report agent creates comprehensive analysis
   - Scores calculated (quality, bias, health)
   - Report stored in database

4. **User Views Results**
   - Dashboard shows statistics
   - Report viewer displays detailed findings
   - Export options available (PDF, JSON, HTML)

## 🔧 Development

### Adding New Agent

1. Create new agent file in `crews/agents/`:
   ```python
   from .base_agent import BaseAnalysisAgent
   
   class CustomAgent(BaseAnalysisAgent):
       def __init__(self):
           super().__init__(name="Custom Agent", description="...")
       
       def analyze(self, df, columns=None):
           # Implementation
           pass
   ```

2. Register in `orchestrator.py`:
   ```python
   from .agents.custom_agent import CustomAgent
   
   self.agents['custom'] = CustomAgent()
   ```

### Running Tests

```bash
cd backend
python test_crew.py
```

## 📝 API Request Examples

### Upload Dataset
```bash
curl -X POST http://localhost:8000/api/datasets/upload/ \
  -F "file=@data.csv" \
  -F "name=My Dataset"
```

### Get Analysis Results
```bash
curl http://localhost:8000/api/datasets/{dataset_id}/results/
```

### Get Dashboard Stats
```bash
curl http://localhost:8000/api/dashboard/stats/
```

## 🔐 Security Considerations

- Enable HTTPS in production
- Set `DEBUG = False` in production
- Use environment variables for sensitive data
- Implement proper authentication/authorization
- Validate all file uploads
- Rate limit API endpoints
- Use PostgreSQL instead of SQLite

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Backend Issues

**ModuleNotFoundError: No module named 'crews'**
- Ensure backend directory is in Python path
- Run: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

**CORS errors**
- Check CORS_ALLOWED_ORIGINS in `.env`
- Verify frontend URL is in whitelist

**Database errors**
- Check database file permissions and `DATABASE_URL` in `.env`

### Frontend Issues

**API calls failing**
- Verify backend is running on correct port
- Check browser console for errors
- Verify API_BASE_URL in services/api.js

**Styling issues**
- Clear browser cache: Ctrl+Shift+Delete
- Rebuild frontend: `npm run build`

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 📧 Support

For support, email support@datasetanalysis.com or open an issue on GitHub.

---

**Built with ❤️ using FastAPI, React, and CrewAI**
