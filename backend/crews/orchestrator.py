"""
Agent Orchestrator - Coordinates and runs all agents using CrewAI
Creates fresh agent instances per call to prevent concurrency issues.
"""
import os
import pandas as pd
import time
import json
import numpy as np
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor

from crewai import Task, Crew, Process, Agent, LLM
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from .tools.data_tools import DataAnalyzer

load_dotenv(override=True)

# ---------------------------------------------------------------------------
# Retry helper for transient LLM/API 503/429 errors
# ---------------------------------------------------------------------------
def _kickoff_with_retry(crew: 'Crew', max_retries: int = 3, base_delay: float = 5.0):
    """Run crew.kickoff() with exponential backoff on transient errors."""
    for attempt in range(max_retries):
        try:
            return crew.kickoff()
        except Exception as e:
            err_str = str(e)
            is_retryable = '503' in err_str or '429' in err_str or 'UNAVAILABLE' in err_str or 'rate' in err_str.lower()
            if is_retryable and attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)  # 5s, 10s, 20s
                print(f"[retry] Groq API transient error (attempt {attempt+1}/{max_retries}), retrying in {delay:.0f}s...")
                time.sleep(delay)
            else:
                raise  # re-raise on final attempt or non-retryable error

# ---------------------------------------------------------------------------
# Output Schemas (Pydantic)
# ---------------------------------------------------------------------------
class ClassifierOutput(BaseModel):
    dataset_type: str = Field(description="The primary dataset type (e.g., numerical, categorical, time_series, sentiment, transaction, mixed)")
    numeric_count: int = Field(description="Number of numeric columns")
    categorical_count: int = Field(description="Number of categorical columns")
    datetime_count: int = Field(description="Number of datetime columns")

class BiasOutput(BaseModel):
    overall_bias_score: float = Field(description="Overall bias score from 0 to 100")
    detected_biases: List[str] = Field(description="List of detected biases or imbalances")

class QualityOutput(BaseModel):
    quality_score: float = Field(description="Overall data quality score from 0 to 100")
    missing_percentage: float = Field(description="Percentage of missing data")

class ReportOutput(BaseModel):
    executive_summary: dict = Field(description="Executive summary with 'overview', 'data_readiness', 'quality_status'")
    conclusion: str = Field(description="Overall conclusion of the analysis")
    recommendations_summary: List[str] = Field(description="List of 3-5 actionable recommendations based on the analysis")


# ---------------------------------------------------------------------------
def _make_llm() -> LLM:
    """Return a fresh LLM instance using Groq exclusively."""
    groq_key = os.getenv("GROQ_API_KEY")
    env_model = os.getenv("LLM_MODEL", "").strip()

    model = env_model if env_model else "groq/llama-3.3-70b-versatile"
    if not model.startswith("groq/") and "/" not in model:
        model = f"groq/{model}"
    return LLM(model=model, api_key=groq_key)


def _make_agents():
    """Create a full set of fresh Agent instances for one orchestrate() call."""
    llm = _make_llm()
    _classifier = Agent(
        role="Classifier",
        goal="Classify the type and structure of the dataset.",
        backstory="You are an expert data engineer who quickly understands the schema, data types, and primary classification of any dataset.",
        llm=llm, verbose=True
    )
    _bias = Agent(
        role="Bias Detector",
        goal="Detect biases and imbalances in the dataset.",
        backstory="You are an AI ethicist and statistician skilled at spotting class imbalances, unrepresented groups, and statistical biases.",
        llm=llm, verbose=True
    )
    _report = Agent(
        role="Report Writer",
        goal="Summarize all analysis findings into a cohesive, executive-level report.",
        backstory="You are a technical writer who translates complex statistical findings into clear, actionable executive reports.",
        llm=llm, verbose=True
    )
    return _classifier, _bias, _report


def _make_chunk_agent() -> Agent:
    """Return a fresh Dataset Analyzer agent — one per thread."""
    return Agent(
        role="Dataset Analyzer",
        goal="Analyze datasets to uncover quality metrics.",
        backstory="You are an expert data analyst.",
        llm=_make_llm(), verbose=False
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
class AgentOrchestrator:
    """Orchestrates parallel CrewAI agents to analyze an uploaded dataset."""

    def orchestrate(self, df: pd.DataFrame, dataset_type: Optional[str] = None, dataset=None) -> Dict[str, Any]:
        """
        Three-phase pipeline:
          Phase 1 – Classify dataset
          Phase 2 – Split into chunks, analyze in parallel
          Phase 3 – Bias detection + Report generation
        """
        start_time = time.time()

        # ---- helpers -------------------------------------------------------
        def handle_np(obj):
            if isinstance(obj, np.integer): return int(obj)
            if isinstance(obj, np.floating): return float(obj)
            if isinstance(obj, np.ndarray): return obj.tolist()
            raise TypeError(f"Not serializable: {type(obj)}")

        def log_status(agent_name: str, status: str):
            if not dataset:
                return
            try:
                from database import SessionLocal
                from models import ExecutionLog
                from datetime import datetime, timezone
                dataset_id = getattr(dataset, 'id', str(dataset))
                now = datetime.now(timezone.utc)
                with SessionLocal() as db_session:
                    log = db_session.query(ExecutionLog).filter_by(
                        dataset_id=dataset_id, agent_name=agent_name
                    ).first()
                    if not log:
                        log = ExecutionLog(
                            dataset_id=dataset_id,
                            agent_name=agent_name,
                            status=status,
                            start_time=now if status == 'running' else None,
                            error=None
                        )
                        db_session.add(log)
                    else:
                        if status == 'running':
                            log.start_time = now
                            log.error = None
                        elif status == 'completed':
                            log.error = None
                        log.status = status
                        if status in ('completed', 'failed'):
                            log.end_time = now
                            if log.start_time:
                                st = log.start_time if log.start_time.tzinfo else log.start_time.replace(tzinfo=timezone.utc)
                                et = log.end_time if log.end_time.tzinfo else log.end_time.replace(tzinfo=timezone.utc)
                                log.execution_time = (et - st).total_seconds()
                    db_session.commit()
            except Exception as exc:
                print(f"[log_status] Warning: {exc}")

        def parse_output(task_output):
            try:
                if hasattr(task_output, 'raw') and isinstance(task_output.raw, str):
                    return json.loads(task_output.raw)
                if task_output.json_dict:
                    return task_output.json_dict
                if hasattr(task_output, 'pydantic') and task_output.pydantic:
                    return task_output.pydantic.model_dump()
            except Exception:
                pass
            return {"raw_output": str(task_output)}

        def make_result(task_output, agent_name, raw_dict=None):
            return {
                'status': 'success',
                'agent': agent_name,
                'data': raw_dict if raw_dict is not None else parse_output(task_output),
                'execution_time': time.time() - start_time
            }

        # ---- dataset summary -----------------------------------------------
        df_head = df.head(5).to_csv(index=False)
        df_info = f"Rows: {df.shape[0]}, Columns: {df.shape[1]}"
        column_types = DataAnalyzer.detect_column_types(df)
        quality_metrics = DataAnalyzer.calculate_quality_metrics(df)

        context_str = (
            f"Dataset Overview:\n{df_info}\n\n"
            f"Column Types: {json.dumps(column_types)}\n\n"
            f"Quality Metrics: {json.dumps(quality_metrics, default=handle_np)}\n\n"
            f"Sample Data:\n{df_head}"
        )

        # ---- PHASE 1: Classification (fresh agents) -----------------------
        _classifier, _bias, _report = _make_agents()
        log_status('Dataset Classifier', 'running')
        classifier_task = Task(
            description=f"Analyze the following dataset metadata and sample to classify its type.\n{context_str}",
            expected_output="JSON object containing dataset_type, numeric_count, categorical_count, datetime_count",
            agent=_classifier,
            output_json=ClassifierOutput
        )
        _kickoff_with_retry(Crew(agents=[_classifier], tasks=[classifier_task], process=Process.sequential, verbose=True))
        classifier_result = parse_output(classifier_task.output)
        dataset_type_detected = classifier_result.get('dataset_type', 'unknown')
        # Immediately log the detected type to DB
        if dataset:
            try:
                from database import SessionLocal
                from models import AnalysisResult
                dataset_id = getattr(dataset, 'id', str(dataset))
                with SessionLocal() as db_session:
                    res = db_session.query(AnalysisResult).filter_by(
                        dataset_id=dataset_id, agent_type='classifier'
                    ).first()
                    if not res:
                        res = AnalysisResult(
                            dataset_id=dataset_id,
                            agent_type='classifier',
                            result_data=classifier_result,
                            status='success'
                        )
                        db_session.add(res)
                    else:
                        res.result_data = classifier_result
                        res.status = 'success'
                    db_session.commit()
            except Exception as e:
                print(f"[classifier result] Warning: {e}")
        log_status('Dataset Classifier', 'completed')

        # ---- PHASE 2: Sequential chunk quality analysis ----------------------
        num_chunks = 1
        chunks = np.array_split(df, num_chunks)
        chunk_results = []

        def analyze_chunk(i, chunk_df):
            """Gets its own fresh agent."""
            agent = _make_chunk_agent()
            log_status(f'Quality Analysis (Chunk {i+1})', 'running')
            chunk_head = chunk_df.head(5).to_csv(index=False)
            chunk_metrics = DataAnalyzer.calculate_quality_metrics(chunk_df)
            chunk_context = (
                f"Chunk {i+1} Overview - Rows: {chunk_df.shape[0]}\n"
                f"Quality Metrics: {json.dumps(chunk_metrics, default=handle_np)}\n"
                f"Sample:\n{chunk_head}"
            )
            chunk_task = Task(
                description=f"Analyze this dataset chunk and return quality_score and missing_percentage.\n{chunk_context}",
                expected_output="JSON object containing quality_score and missing_percentage",
                agent=agent,
                output_json=QualityOutput
            )
            _kickoff_with_retry(Crew(agents=[agent], tasks=[chunk_task], process=Process.sequential, verbose=False))
            log_status(f'Quality Analysis (Chunk {i+1})', 'completed')
            return chunk_task.output

        for i, chunk in enumerate(chunks):
            try:
                res = analyze_chunk(i, chunk)
                chunk_results.append(res)
                if i < len(chunks) - 1:
                    time.sleep(4)  # Small delay between chunk calls
            except Exception as exc:
                print(f"[chunk] Warning: {exc}")

        # Aggregate chunk results
        scores = []
        missings = []
        for out in chunk_results:
            try:
                d = parse_output(out)
                if d.get('quality_score') is not None:
                    scores.append(float(d['quality_score']))
                if d.get('missing_percentage') is not None:
                    missings.append(float(d['missing_percentage']))
            except Exception:
                pass

        avg_quality_score = sum(scores) / len(scores) if scores else 0.0
        avg_missing = sum(missings) / len(missings) if missings else 0.0
        quality_data = {'quality_score': avg_quality_score, 'missing_percentage': avg_missing}

        # ---- PHASE 3: Bias + Report (fresh agents, already created) -------
        log_status('Bias & Report Generation', 'running')
        bias_task = Task(
            description=f"Detect statistical or representational biases in the dataset.\n{context_str}",
            expected_output="JSON object containing overall_bias_score and list of detected_biases",
            agent=_bias,
            output_json=BiasOutput
        )
        report_task = Task(
            description=(
                f"Write an executive report. Aggregated quality score: {avg_quality_score:.1f}.\n{context_str}"
            ),
            expected_output="JSON object with executive_summary and conclusion",
            agent=_report,
            output_json=ReportOutput
        )
        _kickoff_with_retry(Crew(agents=[_bias, _report], tasks=[bias_task, report_task], process=Process.sequential, verbose=True))
        log_status('Bias & Report Generation', 'completed')

        # ---- Assemble final result dict ------------------------------------
        all_results = {
            'classifier': make_result(classifier_task.output, 'classifier'),
            'quality':    make_result(None, 'quality', raw_dict=quality_data),
            'bias':       make_result(bias_task.output, 'bias'),
            'report':     make_result(report_task.output, 'report'),
        }

        for key in ['numerical', 'categorical', 'sentiment', 'time_series',
                    'transaction', 'mixed_data', 'recommendation', 'cleaning']:
            all_results[key] = {'status': 'success', 'data': {}, 'execution_time': 0}

        # Calculate deterministic statistics for dashboard
        total_rows = len(df)
        missing_values_list = []
        columns_stats = []
        for col in df.columns:
            missing_count = int(df[col].isnull().sum())
            missing_pct = round((missing_count / total_rows) * 100, 2) if total_rows > 0 else 0
            unique_count = int(df[col].nunique())
            col_type = column_types.get(col, str(df[col].dtype))
            
            missing_values_list.append({'column': col, 'value': missing_pct})
            columns_stats.append({
                'name': col, 'type': col_type, 'uniqueValues': unique_count, 'missing': f"{missing_pct}%"
            })
            
        missing_values_list = sorted(missing_values_list, key=lambda x: x['value'], reverse=True)[:5]

        # Extract sentiment info
        sentiment_distribution = []
        top_positive_words = []
        top_negative_words = []
        
        dataset_type = all_results['classifier']['data'].get('dataset_type', 'unknown')
        if dataset_type in ['sentiment', 'categorical', 'classification', 'binary', 'multi-class'] or any(c for c in df.columns if c.lower() in ['sentiment', 'label', 'target', 'class', 'category', 'status', 'type', 'result'] or 'sentiment' in c.lower() or 'label' in c.lower()):
            sentiment_col = next((c for c in df.columns if 'sentiment' in c.lower()), None)
            if not sentiment_col:
                # Fallback to general classification targets
                sentiment_col = next((c for c in df.columns if c.lower() in ['label', 'target', 'class', 'category', 'status', 'type', 'result']), None)
            if not sentiment_col:
                # Fallback to rating
                sentiment_col = next((c for c in df.columns if 'rating' in c.lower() and df[c].nunique() <= 10), None)
            if not sentiment_col:
                # Final fallback: pick any low-cardinality column, preferring objects/categories
                obj_cols = [c for c in df.columns if df[c].dtype in ['object', 'category'] and 2 <= df[c].nunique() <= 20]
                if obj_cols:
                    sentiment_col = obj_cols[-1] # pick last (often target is last)
                else:
                    # just pick any low cardinality int column
                    low_card = [c for c in df.columns if 2 <= df[c].nunique() <= 10]
                    if low_card:
                        sentiment_col = low_card[-1]

                
            if sentiment_col:
                val_counts = df[sentiment_col].value_counts()
                total = val_counts.sum()
                for k, v in val_counts.items():
                    label_str = str(k).title()
                    sentiment_distribution.append({
                        'label': label_str,
                        'value': int(v),
                        'percentage': round((v / total) * 100, 1)
                    })
            
            text_col = next((c for c in df.columns if ('text' in c.lower() or 'comment' in c.lower() or 'desc' in c.lower() or 'msg' in c.lower() or 'review' in c.lower()) and 'id' not in c.lower()), None)
            if text_col and sentiment_col:
                try:
                    from .tools.data_tools import TextAnalyzer
                    pos_mask = df[sentiment_col].astype(str).str.contains('pos|5|4', case=False, na=False)
                    neg_mask = df[sentiment_col].astype(str).str.contains('neg|1|2|0', case=False, na=False)
                    
                    pos_texts = df[pos_mask][text_col].dropna().tolist()
                    neg_texts = df[neg_mask][text_col].dropna().tolist()
                    
                    if not pos_texts and not neg_texts:
                        # Fallback if patterns didn't match: take top and bottom 20% by label sort
                        sorted_df = df.sort_values(sentiment_col)
                        n = max(1, len(df) // 5)
                        neg_texts = sorted_df.head(n)[text_col].dropna().tolist()
                        pos_texts = sorted_df.tail(n)[text_col].dropna().tolist()
                    
                    pos_words = TextAnalyzer.extract_keywords(pos_texts, top_n=10)
                    neg_words = TextAnalyzer.extract_keywords(neg_texts, top_n=10)
                    
                    top_positive_words = list(pos_words.keys())
                    top_negative_words = list(neg_words.keys())
                except Exception as e:
                    print(f"Error extracting keywords: {e}")

        all_results['metadata'] = {
            'total_execution_time': time.time() - start_time,
            'dataset_type': dataset_type,
            'missing_values': missing_values_list,
            'columns_info': columns_stats,
            'sentiment_distribution': sentiment_distribution,
            'top_positive_words': top_positive_words,
            'top_negative_words': top_negative_words
        }

        return all_results
