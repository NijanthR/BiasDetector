"""
Datasets router for dataset upload, details, history, analysis, and management
"""
import os
import io
import shutil
import threading
from typing import List, Optional
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import Dataset, AnalysisResult, Report, ExecutionLog
from schemas import (
    DatasetResponse, DatasetDetailResponse, DatasetHistoryResponse,
    DatasetAnalyzeResponse, DatasetDeleteResponse, AnalysisResultResponse
)
from crews.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/datasets", tags=["datasets"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "datasets")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def run_dataset_analysis(dataset_id: str):
    """Background task to analyze a dataset"""
    try:
        with SessionLocal() as db:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if not dataset:
                return

            try:
                dataset.analysis_status = 'processing'
                db.commit()

                # Read dataset file
                file_path = dataset.file
                if not os.path.isabs(file_path):
                    file_path = os.path.join(BASE_DIR, file_path)

                if dataset.file_type == 'csv':
                    df = pd.read_csv(file_path)
                elif dataset.file_type == 'xlsx':
                    df = pd.read_excel(file_path)
                else:
                    df = pd.read_json(file_path)

                # Run agent orchestrator
                orchestrator = AgentOrchestrator()
                results = orchestrator.orchestrate(df, dataset=dataset)

                # Store results
                for agent_key, agent_result in results.items():
                    if agent_key == 'metadata':
                        continue

                    status_str = 'success' if agent_result.get('status') == 'success' else 'failed'
                    res_obj = db.query(AnalysisResult).filter_by(
                        dataset_id=dataset.id, agent_type=agent_key
                    ).first()

                    if not res_obj:
                        res_obj = AnalysisResult(
                            dataset_id=dataset.id,
                            agent_type=agent_key,
                            result_data=agent_result.get('data', {}),
                            visualizations=agent_result.get('visualizations', []),
                            metrics={},
                            execution_time=agent_result.get('execution_time', 0.0),
                            status=status_str,
                            error_message=agent_result.get('error') if status_str == 'failed' else None
                        )
                        db.add(res_obj)
                    else:
                        res_obj.result_data = agent_result.get('data', {})
                        res_obj.visualizations = agent_result.get('visualizations', [])
                        res_obj.execution_time = agent_result.get('execution_time', 0.0)
                        res_obj.status = status_str
                        res_obj.error_message = agent_result.get('error') if status_str == 'failed' else None

                # Generate and store report
                quality_result = results.get('quality', {})
                bias_result = results.get('bias', {})
                report_result = results.get('report', {})
                classifier_result = results.get('classifier', {})
                metadata_result = results.get('metadata', {})

                quality_score = float(quality_result.get('data', {}).get('quality_score', 0))
                bias_score = float(bias_result.get('data', {}).get('overall_bias_score', 0))
                missing_pct = float(quality_result.get('data', {}).get('missing_percentage', 0))
                dataset_type = classifier_result.get('data', {}).get('dataset_type', 'unknown')

                avg_score = (quality_score + (100 - bias_score)) / 2
                if avg_score >= 80:
                    health = 'Excellent'
                elif avg_score >= 60:
                    health = 'Good'
                elif avg_score >= 40:
                    health = 'Fair'
                else:
                    health = 'Poor'

                dataset.dataset_type = dataset_type

                report_data = report_result.get('data', {})
                report_data['top_positive_words'] = metadata_result.get('top_positive_words', [])
                report_data['top_negative_words'] = metadata_result.get('top_negative_words', [])

                # Check if report already exists
                existing_report = db.query(Report).filter_by(dataset_id=dataset.id).first()
                if existing_report:
                    existing_report.title = f"Analysis Report - {dataset.name}"
                    existing_report.dataset_type = dataset_type
                    existing_report.data_quality_score = quality_score
                    existing_report.bias_score = bias_score
                    existing_report.overall_health = health
                    existing_report.summary = report_data
                    existing_report.bias_analysis = bias_result.get('data', {})
                    existing_report.quality_metrics = {
                        'missing_percentage': missing_pct,
                        'quality_score': quality_score,
                        'missing_values': metadata_result.get('missing_values', [])
                    }
                    existing_report.statistics = {
                        'columns': metadata_result.get('columns_info', []),
                        'sentiment_distribution': metadata_result.get('sentiment_distribution', [])
                    }
                    existing_report.recommendations = report_data.get('recommendations_summary', [])
                else:
                    report = Report(
                        dataset_id=dataset.id,
                        title=f"Analysis Report - {dataset.name}",
                        dataset_type=dataset_type,
                        data_quality_score=quality_score,
                        bias_score=bias_score,
                        overall_health=health,
                        summary=report_data,
                        bias_analysis=bias_result.get('data', {}),
                        quality_metrics={
                            'missing_percentage': missing_pct,
                            'quality_score': quality_score,
                            'missing_values': metadata_result.get('missing_values', [])
                        },
                        statistics={
                            'columns': metadata_result.get('columns_info', []),
                            'sentiment_distribution': metadata_result.get('sentiment_distribution', [])
                        },
                        recommendations=report_data.get('recommendations_summary', []),
                    )
                    db.add(report)

                dataset.analysis_status = 'completed'
                db.commit()

            except Exception as e:
                import traceback
                error_msg = str(e)
                try:
                    dataset.analysis_status = 'failed'
                    db.commit()
                except Exception:
                    pass
                print(f"Analysis failed for dataset {dataset_id}: {error_msg}")
                traceback.print_exc()
                try:
                    db.query(ExecutionLog).filter(
                        ExecutionLog.dataset_id == dataset_id,
                        ExecutionLog.status == 'running'
                    ).update({'status': 'failed', 'error': error_msg[:500]})
                    db.commit()
                except Exception:
                    pass
    except Exception as outer_err:
        print(f"Outer exception in run_dataset_analysis for {dataset_id}: {outer_err}")


@router.post("/upload/", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
@router.post("/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db)
):
    """Upload a new dataset and trigger analysis"""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    filename = file.filename or "dataset.csv"
    file_ext = filename.split('.')[-1].lower()

    if file_ext not in ['csv', 'xlsx', 'json']:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Only CSV, XLSX, and JSON are supported"
        )

    # Read content to parse metadata and save
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)

    try:
        buffer = io.BytesIO(contents)
        if file_ext == 'csv':
            df = pd.read_csv(buffer)
        elif file_ext == 'xlsx':
            df = pd.read_excel(buffer)
        elif file_ext == 'json':
            df = pd.read_json(buffer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    # Clean up all previous files in UPLOAD_DIR (session-based storage)
    if os.path.exists(UPLOAD_DIR):
        for old_file in os.listdir(UPLOAD_DIR):
            old_file_path = os.path.join(UPLOAD_DIR, old_file)
            try:
                if os.path.isfile(old_file_path):
                    os.remove(old_file_path)
            except Exception as exc:
                print(f"[upload cleanup] Warning removing old file {old_file}: {exc}")

    # Clean up previous datasets from database for a fresh session
    try:
        prev_datasets = db.query(Dataset).all()
        for prev_d in prev_datasets:
            db.delete(prev_d)
        db.commit()
    except Exception as exc:
        print(f"[upload cleanup] Warning clearing old db datasets: {exc}")

    # Save only the current session's file to disk
    dataset_name = name if name and name.strip() else filename.rsplit('.', 1)[0]
    safe_filename = f"{dataset_name.replace(' ', '_')}_{int(pd.Timestamp.now().timestamp())}.{file_ext}"
    saved_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(saved_path, "wb") as f:
        f.write(contents)

    # Create dataset record
    dataset = Dataset(
        name=dataset_name,
        file=os.path.relpath(saved_path, BASE_DIR).replace('\\', '/'),
        file_type=file_ext,
        rows=len(df),
        columns=len(df.columns),
        columns_info=df.dtypes.astype(str).to_dict(),
        size_mb=round(size_mb, 4),
        analysis_status="pending"
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Trigger background analysis in a thread for reliability
    threading.Thread(target=run_dataset_analysis, args=(dataset.id,), daemon=True).start()

    return dataset


@router.get("/history/", response_model=DatasetHistoryResponse)
@router.get("/history", response_model=DatasetHistoryResponse)
def get_dataset_history(db: Session = Depends(get_db)):
    """Get recent dataset upload history"""
    datasets = db.query(Dataset).order_by(Dataset.uploaded_at.desc()).limit(20).all()
    return {
        "total": len(datasets),
        "datasets": datasets
    }


@router.post("/{dataset_id}/analyze/", response_model=DatasetAnalyzeResponse)
@router.post("/{dataset_id}/analyze", response_model=DatasetAnalyzeResponse)
def trigger_analysis(dataset_id: str, db: Session = Depends(get_db)):
    """Trigger analysis of a dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    threading.Thread(target=run_dataset_analysis, args=(dataset.id,), daemon=True).start()

    return {
        "status": "Analysis started",
        "dataset_id": dataset.id
    }


@router.get("/{dataset_id}/results/")
@router.get("/{dataset_id}/results")
def get_dataset_results(dataset_id: str, db: Session = Depends(get_db)):
    """Get analysis results for a dataset"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    results = db.query(AnalysisResult).filter(AnalysisResult.dataset_id == dataset.id).all()
    serialized_results = []
    for r in results:
        serialized_results.append({
            "id": r.id,
            "dataset": r.dataset_id,
            "agent_type": r.agent_type,
            "result_data": r.result_data or {},
            "visualizations": r.visualizations or [],
            "metrics": r.metrics or {},
            "execution_time": r.execution_time or 0.0,
            "status": r.status,
            "error_message": r.error_message,
            "created_at": r.created_at.isoformat() if r.created_at else None
        })

    return {
        "dataset_id": dataset.id,
        "analysis_results": serialized_results
    }


@router.get("/{dataset_id}/details/", response_model=DatasetDetailResponse)
@router.get("/{dataset_id}/details", response_model=DatasetDetailResponse)
def get_dataset_details(dataset_id: str, db: Session = Depends(get_db)):
    """Get detailed dataset info with analysis results"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/", response_model=List[DatasetResponse])
@router.get("", response_model=List[DatasetResponse])
def list_datasets(db: Session = Depends(get_db)):
    """List all datasets"""
    return db.query(Dataset).order_by(Dataset.uploaded_at.desc()).all()


@router.get("/{dataset_id}/", response_model=DatasetResponse)
@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Get a single dataset by ID"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.delete("/{dataset_id}/", response_model=DatasetDeleteResponse)
@router.delete("/{dataset_id}", response_model=DatasetDeleteResponse)
def delete_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """Delete a dataset and associated data"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Remove physical file if it exists
    file_path = dataset.file
    if not os.path.isabs(file_path):
        file_path = os.path.join(BASE_DIR, file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    deleted_id = dataset.id
    db.delete(dataset)
    db.commit()

    return {
        "message": "Dataset deleted successfully",
        "dataset_id": deleted_id
    }
