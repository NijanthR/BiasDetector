"""
Pydantic schemas for request validation and response serialization
"""
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


class DatasetBase(BaseModel):
    name: str
    file_type: str = "csv"
    dataset_type: Optional[str] = None
    rows: int = 0
    columns: int = 0
    columns_info: Dict[str, Any] = Field(default_factory=dict)
    size_mb: float = 0.0
    analysis_status: str = "pending"


class DatasetResponse(DatasetBase):
    id: str
    file: str
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisResultResponse(BaseModel):
    id: str
    dataset: str
    agent_type: str
    result_data: Dict[str, Any] = Field(default_factory=dict)
    visualizations: List[Any] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = 0.0
    status: str = "success"
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetDetailResponse(DatasetResponse):
    analysis_results: List[AnalysisResultResponse] = Field(default_factory=list)


class DatasetHistoryResponse(BaseModel):
    total: int
    datasets: List[DatasetResponse]


class DatasetAnalyzeResponse(BaseModel):
    status: str
    dataset_id: str


class DatasetDeleteResponse(BaseModel):
    message: str
    dataset_id: str


class DatasetSummaryInReport(BaseModel):
    id: str
    name: str
    rows: int
    columns: int


class ReportResponse(BaseModel):
    id: str
    dataset: DatasetSummaryInReport
    title: str
    description: str = ""
    dataset_type: str = ""
    data_quality_score: float = 0.0
    bias_score: float = 0.0
    overall_health: str = "unknown"
    summary: Dict[str, Any] = Field(default_factory=dict)
    bias_analysis: Dict[str, Any] = Field(default_factory=dict)
    quality_metrics: Dict[str, Any] = Field(default_factory=dict)
    statistics: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[Any] = Field(default_factory=list)
    visualizations: List[Any] = Field(default_factory=list)
    format: str = "pdf"
    file: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LatestReportsResponse(BaseModel):
    total: int
    reports: List[ReportResponse]


class ReportExportRequest(BaseModel):
    format: Optional[str] = "json"


class ExecutionLogItem(BaseModel):
    agent: str
    status: str
    time: str
    execution_time: Optional[float] = None
    error: Optional[str] = None


class RecentAnalysisItem(BaseModel):
    id: str
    name: str
    type: Optional[str] = None
    uploaded: str
    rows: int
    columns: int


class DashboardStatsResponse(BaseModel):
    total_datasets: int
    total_reports: int
    analysis_in_progress: int
    recent_analyses: List[RecentAnalysisItem]
    active_logs: List[ExecutionLogItem]
    active_dataset_status: Optional[str] = None


class DashboardOverviewResponse(BaseModel):
    total_datasets: int
    completed_analyses: int
    failed_analyses: int
    average_quality_score: float
    average_bias_score: float
    success_rate: float


class LogItem(BaseModel):
    id: str
    dataset_name: str
    agent: str
    status: str
    time: str
    execution_time: Optional[float] = None
    error: Optional[str] = None


class DashboardLogsResponse(BaseModel):
    logs: List[LogItem]
