"""
Reports router for fetching and exporting analysis reports
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Report, Dataset
from schemas import (
    ReportResponse, LatestReportsResponse, ReportExportRequest
)

router = APIRouter(prefix="/reports", tags=["reports"])


def serialize_report(report: Report) -> dict:
    """Format report dict with nested dataset summary matching frontend expectations"""
    dataset_info = {
        "id": report.dataset.id if report.dataset else "",
        "name": report.dataset.name if report.dataset else "Unknown",
        "rows": report.dataset.rows if report.dataset else 0,
        "columns": report.dataset.columns if report.dataset else 0,
    }

    return {
        "id": report.id,
        "dataset": dataset_info,
        "title": report.title,
        "description": report.description or "",
        "dataset_type": report.dataset_type or "",
        "data_quality_score": report.data_quality_score or 0.0,
        "bias_score": report.bias_score or 0.0,
        "overall_health": report.overall_health or "unknown",
        "summary": report.summary or {},
        "bias_analysis": report.bias_analysis or {},
        "quality_metrics": report.quality_metrics or {},
        "statistics": report.statistics or {},
        "recommendations": report.recommendations or [],
        "visualizations": report.visualizations or [],
        "format": report.format or "pdf",
        "file": report.file,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "updated_at": report.updated_at.isoformat() if report.updated_at else None,
    }


@router.get("/latest_reports/")
@router.get("/latest_reports")
@router.get("/latest/")
@router.get("/latest")
def get_latest_reports(db: Session = Depends(get_db)):
    """Get latest generated reports"""
    reports = db.query(Report).order_by(Report.created_at.desc()).limit(10).all()
    serialized = [serialize_report(r) for r in reports]
    return {
        "total": len(reports),
        "reports": serialized
    }


@router.get("/")
@router.get("")
def list_reports(db: Session = Depends(get_db)):
    """List all reports"""
    reports = db.query(Report).order_by(Report.created_at.desc()).all()
    return [serialize_report(r) for r in reports]


@router.get("/{report_id}/")
@router.get("/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)):
    """Get a single report by ID (or dataset ID)"""
    report = db.query(Report).filter(
        (Report.id == report_id) | (Report.dataset_id == report_id)
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return serialize_report(report)


@router.post("/{report_id}/export/")
@router.post("/{report_id}/export")
def export_report(report_id: str, payload: ReportExportRequest = ReportExportRequest(), db: Session = Depends(get_db)):
    """Export report to specified format"""
    report = db.query(Report).filter(
        (Report.id == report_id) | (Report.dataset_id == report_id)
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    format_type = payload.format or "json"
    if format_type.lower() == "json":
        return serialize_report(report)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Export format '{format_type}' is not supported yet"
    )
