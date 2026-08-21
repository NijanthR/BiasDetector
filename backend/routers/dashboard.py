"""
Dashboard router for platform metrics, overview, and agent logs
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Dataset, Report, ExecutionLog
from schemas import (
    DashboardStatsResponse, DashboardOverviewResponse, DashboardLogsResponse
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats/", response_model=DashboardStatsResponse)
@router.get("/stats", response_model=DashboardStatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Get dashboard overview statistics, recent analyses, and active agent execution logs"""
    total_datasets = db.query(Dataset).count()
    total_reports = db.query(Report).count()
    analysis_in_progress = db.query(Dataset).filter(
        Dataset.analysis_status.in_(["pending", "processing"])
    ).count()

    recent_completed = db.query(Dataset).filter(
        Dataset.analysis_status == "completed"
    ).order_by(Dataset.updated_at.desc()).limit(5).all()

    recent_data = [{
        "id": str(d.id),
        "name": d.name,
        "type": d.dataset_type,
        "uploaded": d.uploaded_at.isoformat() if d.uploaded_at else datetime.now(timezone.utc).isoformat(),
        "rows": d.rows or 0,
        "columns": d.columns or 0,
    } for d in recent_completed]

    # Active logs: Check currently processing/pending dataset first
    active_dataset = db.query(Dataset).filter(
        Dataset.analysis_status.in_(["pending", "processing"])
    ).order_by(Dataset.uploaded_at.desc()).first()

    if not active_dataset:
        # Fallback to dataset updated within the last 5 minutes or latest completed
        five_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        active_dataset = db.query(Dataset).filter(
            Dataset.analysis_status.in_(["completed", "failed"]),
            Dataset.updated_at >= five_mins_ago
        ).order_by(Dataset.updated_at.desc()).first()

    active_logs = []
    if active_dataset:
        logs = db.query(ExecutionLog).filter(
            ExecutionLog.dataset_id == active_dataset.id
        ).order_by(ExecutionLog.created_at.asc()).all()

        active_logs = [{
            "agent": log.agent_name,
            "status": log.status,
            "time": log.created_at.isoformat() if log.created_at else datetime.now(timezone.utc).isoformat(),
            "execution_time": log.execution_time,
            "error": log.error if log.error else None,
        } for log in logs]

    return {
        "total_datasets": total_datasets,
        "total_reports": total_reports,
        "analysis_in_progress": analysis_in_progress,
        "recent_analyses": recent_data,
        "active_logs": active_logs,
        "active_dataset_status": active_dataset.analysis_status if active_dataset else None,
    }


@router.get("/overview/", response_model=DashboardOverviewResponse)
@router.get("/overview", response_model=DashboardOverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    """Get platform overview metrics"""
    total_datasets = db.query(Dataset).count()
    completed = db.query(Dataset).filter(Dataset.analysis_status == "completed").count()
    failed = db.query(Dataset).filter(Dataset.analysis_status == "failed").count()

    reports = db.query(Report).all()
    avg_quality = sum(r.data_quality_score or 0 for r in reports) / len(reports) if reports else 0.0
    avg_bias = sum(r.bias_score or 0 for r in reports) / len(reports) if reports else 0.0
    success_rate = round((completed / total_datasets * 100), 2) if total_datasets > 0 else 0.0

    return {
        "total_datasets": total_datasets,
        "completed_analyses": completed,
        "failed_analyses": failed,
        "average_quality_score": round(avg_quality, 2),
        "average_bias_score": round(avg_bias, 2),
        "success_rate": success_rate,
    }


@router.get("/logs/", response_model=DashboardLogsResponse)
@router.get("/logs", response_model=DashboardLogsResponse)
def get_logs(db: Session = Depends(get_db)):
    """Get system-wide agent execution logs"""
    logs = db.query(ExecutionLog).order_by(ExecutionLog.created_at.desc()).limit(100).all()
    logs_data = [{
        "id": str(log.id),
        "dataset_name": log.dataset.name if log.dataset else "Unknown",
        "agent": log.agent_name,
        "status": log.status,
        "time": log.created_at.isoformat() if log.created_at else datetime.now(timezone.utc).isoformat(),
        "execution_time": log.execution_time,
        "error": log.error if log.error else None,
    } for log in logs]

    return {"logs": logs_data}
