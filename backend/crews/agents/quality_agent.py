"""
Quality Agent - Analyzes data quality
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import DataAnalyzer
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class QualityAgent(BaseAnalysisAgent):
    """Analyzes data quality metrics"""
    
    def __init__(self):
        super().__init__(
            name="Quality Agent",
            description="Analyzes data quality metrics"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Analyze data quality"""
        
        # Calculate quality metrics
        quality_metrics = DataAnalyzer.calculate_quality_metrics(df)
        
        # Check for consistency issues
        consistency_issues = self._check_consistency(df)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(df, quality_metrics, consistency_issues)
        
        # Identify problem areas
        problem_areas = self._identify_problem_areas(df, quality_metrics)
        
        return {
            'metrics': quality_metrics,
            'quality_score': quality_score,
            'consistency_issues': consistency_issues,
            'problem_areas': problem_areas,
            'recommendations': self._generate_recommendations(quality_metrics, consistency_issues),
        }
    
    def _check_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Check for data consistency issues"""
        issues = {
            'data_type_issues': [],
            'range_issues': [],
            'format_issues': [],
        }
        
        numeric_cols = self._get_numeric_columns(df)
        
        # Check for negative values in columns that shouldn't have them
        for col in numeric_cols:
            if (df[col] < 0).any():
                if any(keyword in col.lower() for keyword in ['amount', 'price', 'quantity']):
                    issues['range_issues'].append(f"{col}: Contains negative values")
        
        return issues
    
    def _calculate_quality_score(self, df: pd.DataFrame, metrics: Dict, issues: Dict) -> float:
        """Calculate overall quality score (0-100)"""
        
        # Start with perfect score
        score = 100.0
        
        # Deduct for missing data
        score -= metrics['missing_percentage'] * 0.5
        
        # Deduct for duplicates
        score -= metrics['duplicate_percentage'] * 0.3
        
        # Deduct for consistency issues
        score -= len(issues['data_type_issues']) * 5
        score -= len(issues['range_issues']) * 5
        score -= len(issues['format_issues']) * 3
        
        return max(0, min(100, score))
    
    def _identify_problem_areas(self, df: pd.DataFrame, metrics: Dict) -> list:
        """Identify columns with quality issues"""
        problems = []
        
        for col, missing_count in metrics['column_missing'].items():
            missing_pct = (missing_count / len(df)) * 100
            
            if missing_pct > 50:
                problems.append({
                    'column': col,
                    'issue': 'High missing values',
                    'value': missing_pct,
                    'severity': 'critical',
                })
            elif missing_pct > 20:
                problems.append({
                    'column': col,
                    'issue': 'Moderate missing values',
                    'value': missing_pct,
                    'severity': 'warning',
                })
        
        return problems
    
    def _generate_recommendations(self, metrics: Dict, issues: Dict) -> list:
        """Generate quality improvement recommendations"""
        recommendations = []
        
        if metrics['missing_percentage'] > 20:
            recommendations.append("Handle missing values: Consider imputation or removal")
        
        if metrics['duplicate_percentage'] > 5:
            recommendations.append("Remove duplicate records to improve data integrity")
        
        if metrics['completeness'] < 80:
            recommendations.append("Improve data completeness by addressing missing values")
        
        if len(issues['range_issues']) > 0:
            recommendations.append("Validate data ranges and fix out-of-range values")
        
        return recommendations
