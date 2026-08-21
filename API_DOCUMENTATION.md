# API Documentation

Complete REST API documentation for the Multi-Agent Dataset Analysis Platform.

## Base URL

Development: `http://localhost:8000/api`
Production: `https://yourdomain.com/api`

## Interactive Documentation

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Authentication

Open API (Public / Internal). For production, JWT bearer authentication can be enabled.

## Response Format

All responses are in JSON format.

### Success Response
```json
{
  "id": "uuid",
  "data": "...",
  "message": "Success"
}
```

### Error Response
```json
{
  "error": "Error description",
  "status": 400,
  "details": "Additional details"
}
```

## Status Codes

- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Server Error

---

## Datasets Endpoints

### Upload Dataset

**POST** `/datasets/upload/`

Upload a new dataset for analysis.

**Parameters:**
- `file` (required) - CSV, XLSX, or JSON file (max 100MB)
- `name` (optional) - Dataset name

**Example:**
```bash
curl -X POST http://localhost:8000/api/datasets/upload/ \
  -F "file=@data.csv" \
  -F "name=My Dataset"
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Dataset",
  "file": "path/to/file.csv",
  "size_mb": 2.5,
  "rows": 1000,
  "columns": 15,
  "uploaded_at": "2024-01-15T10:30:00Z",
  "analysis_status": "processing"
}
```

### List Datasets

**GET** `/datasets/`

Retrieve all uploaded datasets.

**Query Parameters:**
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20)
- `status` - Filter by status (pending, processing, completed, failed)

**Example:**
```bash
curl http://localhost:8000/api/datasets/?page=1&limit=20
```

**Response:**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/datasets/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "My Dataset",
      "rows": 1000,
      "columns": 15,
      "size_mb": 2.5,
      "status": "completed",
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Get Dataset Details

**GET** `/datasets/{id}/`

Get detailed information about a specific dataset including analysis results.

**Path Parameters:**
- `id` - Dataset UUID

**Example:**
```bash
curl http://localhost:8000/api/datasets/550e8400-e29b-41d4-a716-446655440000/
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Dataset",
  "file": "path/to/file.csv",
  "size_mb": 2.5,
  "rows": 1000,
  "columns": 15,
  "columns_info": {
    "column1": "numeric",
    "column2": "categorical"
  },
  "uploaded_at": "2024-01-15T10:30:00Z",
  "analysis_status": "completed",
  "analysis_results": [
    {
      "id": "uuid",
      "agent": "quality_agent",
      "result_data": {...},
      "metrics": {...}
    }
  ]
}
```

### Get Analysis Results

**GET** `/datasets/{id}/results/`

Get all analysis results for a dataset.

**Example:**
```bash
curl http://localhost:8000/api/datasets/550e8400-e29b-41d4-a716-446655440000/results/
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "agent": "quality_agent",
      "result_data": {
        "quality_score": 85,
        "missing_values": 2.5,
        "duplicates": 0
      },
      "metrics": {
        "accuracy": 0.95,
        "precision": 0.92
      },
      "execution_time": 5.23
    }
  ],
  "total_agents": 12,
  "completed_agents": 12,
  "total_execution_time": 45.67
}
```

### Trigger Analysis

**POST** `/datasets/{id}/analyze/`

Manually trigger analysis for a dataset.

**Example:**
```bash
curl -X POST http://localhost:8000/api/datasets/550e8400-e29b-41d4-a716-446655440000/analyze/
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "message": "Analysis started"
}
```

### Dataset History

**GET** `/datasets/history/`

Get upload history (last 20 datasets).

**Query Parameters:**
- `limit` - Number of records (default: 20)

**Example:**
```bash
curl http://localhost:8000/api/datasets/history/?limit=20
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid",
      "name": "Dataset Name",
      "type": "numerical",
      "rows": 1000,
      "columns": 15,
      "status": "completed",
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Delete Dataset

**DELETE** `/datasets/{id}/`

Delete a dataset and all associated data.

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/datasets/550e8400-e29b-41d4-a716-446655440000/
```

**Response:**
```json
{
  "message": "Dataset deleted successfully"
}
```

---

## Reports Endpoints

### List Reports

**GET** `/reports/`

Get all generated reports.

**Query Parameters:**
- `page` - Page number
- `limit` - Items per page

**Example:**
```bash
curl http://localhost:8000/api/reports/
```

**Response:**
```json
{
  "count": 42,
  "results": [
    {
      "id": "uuid",
      "dataset_id": "uuid",
      "quality_score": 85,
      "bias_score": 20,
      "overall_health": "excellent",
      "generated_at": "2024-01-15T10:35:00Z"
    }
  ]
}
```

### Get Specific Report

**GET** `/reports/{id}/`

Get detailed report information.

**Example:**
```bash
curl http://localhost:8000/api/reports/550e8400-e29b-41d4-a716-446655440000/
```

**Response:**
```json
{
  "id": "uuid",
  "dataset_id": "uuid",
  "dataset_name": "My Dataset",
  "quality_score": 85,
  "bias_score": 20,
  "overall_health": "excellent",
  "executive_summary": "Dataset quality is excellent with minimal bias issues.",
  "dataset_overview": {
    "rows": 1000,
    "columns": 15,
    "types": {
      "numeric": 8,
      "categorical": 5,
      "datetime": 2
    }
  },
  "key_findings": [
    "Column X has 2.5% missing values",
    "Class imbalance detected in target column"
  ],
  "recommendations": [
    "Impute missing values in column X",
    "Consider using class weights in model training"
  ],
  "generated_at": "2024-01-15T10:35:00Z"
}
```

### Latest Reports

**GET** `/reports/latest/`

Get the latest reports (top 10).

**Query Parameters:**
- `limit` - Number of reports (default: 10)

**Example:**
```bash
curl http://localhost:8000/api/reports/latest/?limit=10
```

### Export Report

**POST** `/reports/{id}/export/`

Export report in specified format.

**Parameters:**
- `format` - Export format (json, csv, pdf, html)

**Example:**
```bash
curl -X POST http://localhost:8000/api/reports/550e8400-e29b-41d4-a716-446655440000/export/ \
  -H "Content-Type: application/json" \
  -d '{"format": "pdf"}'
```

**Response:**
```json
{
  "url": "http://localhost:8000/media/reports/report_uuid.pdf",
  "format": "pdf",
  "size_mb": 1.2
}
```

---

## Dashboard Endpoints

### Dashboard Statistics

**GET** `/dashboard/stats/`

Get platform-wide statistics.

**Example:**
```bash
curl http://localhost:8000/api/dashboard/stats/
```

**Response:**
```json
{
  "total_datasets": 42,
  "total_reports": 40,
  "analysis_in_progress": 2,
  "datasets_by_status": {
    "completed": 40,
    "processing": 2,
    "failed": 0,
    "pending": 0
  },
  "recent_analyses": [
    {
      "id": "uuid",
      "name": "Dataset Name",
      "type": "numerical",
      "rows": 1000,
      "columns": 15,
      "uploaded_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### Dashboard Overview

**GET** `/dashboard/overview/`

Get platform overview with metrics.

**Example:**
```bash
curl http://localhost:8000/api/dashboard/overview/
```

**Response:**
```json
{
  "completion_rate": 95.2,
  "average_quality_score": 82.3,
  "average_bias_score": 18.5,
  "success_rate": 98.1,
  "total_analyses_completed": 40,
  "total_agents_executed": 480,
  "average_execution_time": 45.67
}
```

---

## Analysis Result Details

### Quality Agent Result

```json
{
  "agent": "quality_agent",
  "quality_score": 85,
  "missing_percentage": 2.5,
  "duplicate_percentage": 0.1,
  "column_missing": {
    "column_name": 5
  },
  "problem_areas": [
    "Column X has 5% missing values",
    "Column Y has duplicate entries"
  ],
  "recommendations": [
    "Impute missing values",
    "Remove duplicates"
  ]
}
```

### Bias Agent Result

```json
{
  "agent": "bias_agent",
  "overall_bias_score": 20,
  "biased_columns": ["target_column"],
  "fairness_report": {
    "critical_findings": [
      "Target column has class imbalance (70:30)"
    ],
    "entropy": 0.88
  }
}
```

### Numerical Agent Result

```json
{
  "agent": "numerical_agent",
  "statistics": {
    "mean": 150.5,
    "median": 155,
    "std": 25.3,
    "min": 50,
    "max": 300
  },
  "correlation_analysis": {...},
  "high_correlations": [
    {"var1": "x", "var2": "y", "correlation": 0.92}
  ],
  "outliers_detected": 15,
  "visualization_data": {...}
}
```

### Categorical Agent Result

```json
{
  "agent": "categorical_agent",
  "frequency_analysis": {
    "category_a": 450,
    "category_b": 350,
    "category_c": 200
  },
  "imbalance_analysis": {
    "imbalance_ratio": 2.25,
    "dominant_class": "category_a"
  },
  "visualization_data": {...}
}
```

### Sentiment Agent Result

```json
{
  "agent": "sentiment_agent",
  "sentiment_distribution": {
    "positive": 45,
    "neutral": 35,
    "negative": 20
  },
  "polarity_score": 0.65,
  "subjectivity_score": 0.72,
  "keywords": ["good", "excellent", "recommend"],
  "topic_analysis": {...}
}
```

### Time Series Agent Result

```json
{
  "agent": "time_series_agent",
  "trend": "increasing",
  "slope": 0.5,
  "seasonality_detected": true,
  "period": 12,
  "anomalies": 3,
  "forecast_readiness_score": 78,
  "time_range": {
    "start": "2023-01-01",
    "end": "2024-01-15",
    "periods": 380
  }
}
```

### Transaction Agent Result

```json
{
  "agent": "transaction_agent",
  "total_transactions": 5000,
  "total_value": 125000.50,
  "average_transaction": 25.00,
  "fraud_indicators": {
    "suspicious_count": 15,
    "fraud_risk_score": 0.15
  },
  "customer_analysis": {
    "total_customers": 250,
    "repeat_customers": 150
  }
}
```

### Mixed Data Agent Result

```json
{
  "agent": "mixed_data_agent",
  "feature_interactions": [
    {
      "feature1": "x",
      "feature2": "y",
      "interaction_strength": 0.85
    }
  ],
  "encoding_suggestions": {
    "column_name": "one_hot_encoding"
  },
  "feature_importance": {
    "column_x": 0.35,
    "column_y": 0.28
  }
}
```

### Recommendation Agent Result

```json
{
  "agent": "recommendation_agent",
  "data_cleaning": [
    "Remove 5 duplicate rows",
    "Impute 25 missing values"
  ],
  "preprocessing": [
    "Normalize numerical features",
    "Encode categorical variables"
  ],
  "model_recommendations": [
    "Use ensemble methods",
    "Consider class weighting"
  ],
  "priority_actions": [
    {
      "action": "Handle class imbalance",
      "priority": "high",
      "impact": "improved_accuracy"
    }
  ]
}
```

### Cleaning Agent Result

```json
{
  "agent": "cleaning_agent",
  "missing_value_strategies": {
    "column_x": "mean_imputation",
    "column_y": "forward_fill"
  },
  "duplicate_handling": "remove_duplicates",
  "outlier_handling": {
    "method": "iqr",
    "threshold": 1.5
  },
  "standardization_suggestions": [
    "Normalize numerical features",
    "Standardize date formats"
  ]
}
```

### Report Agent Result

```json
{
  "agent": "report_agent",
  "executive_summary": "Dataset quality is high...",
  "dataset_overview": {...},
  "quality_score_summary": "85/100 - Excellent",
  "key_findings": [...],
  "conclusion": "Ready for ML pipeline..."
}
```

---

## Error Handling

### Common Errors

**400 - Bad Request**
```json
{
  "error": "Invalid file format",
  "details": "File must be CSV, XLSX, or JSON"
}
```

**404 - Not Found**
```json
{
  "error": "Dataset not found",
  "id": "invalid-uuid"
}
```

**500 - Server Error**
```json
{
  "error": "Internal server error",
  "message": "Error processing dataset"
}
```

---

## Rate Limiting

Current rate limits (future implementation):
- Uploads: 10 per hour per IP
- API calls: 1000 per hour per IP

---

## Webhooks (Future)

Configure webhooks for events:
- `dataset.uploaded`
- `analysis.completed`
- `analysis.failed`

---

## Code Examples

### Python (Requests)

```python
import requests

API_URL = "http://localhost:8000/api"

# Upload dataset
with open('data.csv', 'rb') as f:
    files = {'file': f}
    data = {'name': 'My Dataset'}
    response = requests.post(
        f"{API_URL}/datasets/upload/",
        files=files,
        data=data
    )
    dataset_id = response.json()['id']

# Get analysis results
response = requests.get(f"{API_URL}/datasets/{dataset_id}/results/")
results = response.json()

# Get report
response = requests.get(f"{API_URL}/reports/latest/")
reports = response.json()

print(reports)
```

### JavaScript (Fetch)

```javascript
const API_URL = "http://localhost:8000/api";

// Upload dataset
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('name', 'My Dataset');

const response = await fetch(`${API_URL}/datasets/upload/`, {
  method: 'POST',
  body: formData
});

const dataset = await response.json();
const datasetId = dataset.id;

// Get analysis results
const resultsResponse = await fetch(
  `${API_URL}/datasets/${datasetId}/results/`
);
const results = await resultsResponse.json();

console.log(results);
```

### cURL

```bash
# Upload
curl -X POST http://localhost:8000/api/datasets/upload/ \
  -F "file=@data.csv" \
  -F "name=Dataset"

# Get results
curl http://localhost:8000/api/datasets/550e8400-e29b-41d4-a716-446655440000/results/

# Get reports
curl http://localhost:8000/api/reports/latest/
```

---

## Pagination

List endpoints support pagination:

```json
{
  "count": 42,
  "next": "http://localhost:8000/api/datasets/?page=2",
  "previous": null,
  "results": [...]
}
```

Query parameters:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20, max: 100)

---

## Filtering and Sorting

Supported filters:
- `status` - Dataset status
- `uploaded_at` - Upload date range
- `dataset_type` - Type of dataset

Example:
```bash
curl "http://localhost:8000/api/datasets/?status=completed&dataset_type=numerical"
```

---

## Additional Resources

- [OpenAPI/Swagger Docs](http://localhost:8000/api/schema/)
- [API Postman Collection](./postman_collection.json)
- [Main README](../README.md)

---

## Support

For API issues or questions, refer to documentation or contact support.
