"""
Categorical Agent - Analyzes categorical data
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import DataAnalyzer
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency


class CategoricalAgent(BaseAnalysisAgent):
    """Analyzes categorical data"""
    
    def __init__(self):
        super().__init__(
            name="Categorical Agent",
            description="Analyzes categorical data"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Analyze categorical data"""
        
        categorical_cols = columns if columns else self._get_categorical_columns(df)
        
        if not categorical_cols:
            return {'message': 'No categorical columns found'}
        
        analysis_results = {
            'column_analysis': {},
            'frequency_analysis': {},
            'imbalance_analysis': {},
        }
        
        for col in categorical_cols:
            # Get value counts
            value_counts = df[col].value_counts()
            
            # Frequency analysis
            analysis_results['frequency_analysis'][col] = value_counts.head(10).to_dict()
            
            # Imbalance analysis
            analysis_results['imbalance_analysis'][col] = DataAnalyzer.detect_class_imbalance(df, col)
            
            # Column analysis
            analysis_results['column_analysis'][col] = {
                'unique_values': int(df[col].nunique()),
                'cardinality_ratio': float(df[col].nunique() / len(df)),
                'top_values': value_counts.head(5).to_dict(),
                'entropy': DataAnalyzer.calculate_entropy(df, col),
            }
        
        # Prepare visualization data
        analysis_results['visualization_data'] = self._prepare_visualization_data(df, categorical_cols)
        
        return analysis_results
    
    def _prepare_visualization_data(self, df: pd.DataFrame, categorical_cols: list) -> Dict[str, Any]:
        """Prepare data for visualizations"""
        
        viz_data = {
            'pie_charts': {},
            'bar_charts': {},
        }
        
        for col in categorical_cols[:5]:  # Limit to first 5
            value_counts = df[col].value_counts().head(10)
            
            viz_data['pie_charts'][col] = {
                'labels': value_counts.index.tolist(),
                'values': value_counts.values.tolist(),
            }
            
            viz_data['bar_charts'][col] = {
                'categories': value_counts.index.tolist(),
                'values': value_counts.values.tolist(),
            }
        
        return viz_data
