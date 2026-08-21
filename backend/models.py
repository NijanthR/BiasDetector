"""
SQLAlchemy database models for the dataset analysis platform
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Text, JSON, DateTime,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_current_time():
    return datetime.now(timezone.utc)


class Dataset(Base):
    """Model for storing uploaded datasets"""
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    file = Column(String(500), nullable=False)
    file_type = Column(String(10), default="csv")
    dataset_type = Column(String(50), nullable=True)

    rows = Column(Integer, default=0)
    columns = Column(Integer, default=0)
    columns_info = Column(JSON, default=dict)

    size_mb = Column(Float, default=0.0)
    analysis_status = Column(String(20), default="pending")  # pending, processing, completed, failed

    uploaded_at = Column(DateTime, default=get_current_time)
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time)

    # Relationships
    analysis_results = relationship(
        "AnalysisResult",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="desc(AnalysisResult.created_at)"
    )
    reports = relationship(
        "Report",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="desc(Report.created_at)"
    )
    execution_logs = relationship(
        "ExecutionLog",
        back_populates="dataset",
        cascade="all, delete-orphan",
        order_by="ExecutionLog.created_at"
    )

    def __repr__(self):
        return f"<Dataset {self.name} ({self.file_type})>"


class AnalysisResult(Base):
    """Model for storing analysis results from agents"""
    __tablename__ = "analysis_results"
    __table_args__ = (
        UniqueConstraint("dataset_id", "agent_type", name="uq_dataset_agent_type"),
    )

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    agent_type = Column(String(50), nullable=False)

    result_data = Column(JSON, default=dict)
    visualizations = Column(JSON, default=list)
    metrics = Column(JSON, default=dict)

    execution_time = Column(Float, default=0.0)
    status = Column(String(20), default="success")  # success, failed
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=get_current_time)

    # Relationships
    dataset = relationship("Dataset", back_populates="analysis_results")

    def __repr__(self):
        return f"<AnalysisResult {self.agent_type} - {self.status}>"


class Report(Base):
    """Model for storing generated reports"""
    __tablename__ = "reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False)
    description = Column(Text, default="")

    # Summary data
    dataset_type = Column(String(50), default="")
    data_quality_score = Column(Float, default=0.0)
    bias_score = Column(Float, default=0.0)
    overall_health = Column(String(20), default="unknown")

    # Report content
    summary = Column(JSON, default=dict)
    bias_analysis = Column(JSON, default=dict)
    quality_metrics = Column(JSON, default=dict)
    statistics = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)
    visualizations = Column(JSON, default=list)

    format = Column(String(10), default="pdf")
    file = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=get_current_time)
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time)

    # Relationships
    dataset = relationship("Dataset", back_populates="reports")

    def __repr__(self):
        return f"<Report {self.title}>"


class ExecutionLog(Base):
    """Model for tracking agent execution"""
    __tablename__ = "execution_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    dataset_id = Column(String(36), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)

    agent_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # pending, running, completed, failed

    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    execution_time = Column(Float, nullable=True)

    output = Column(JSON, default=dict)
    error = Column(Text, default="")

    created_at = Column(DateTime, default=get_current_time)

    # Relationships
    dataset = relationship("Dataset", back_populates="execution_logs")

    def __repr__(self):
        return f"<ExecutionLog {self.agent_name} - {self.status}>"
