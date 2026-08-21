"""
Numerical Agent - Analyzes numerical data
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import DataAnalyzer
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class NumericalAgent(BaseAnalysisAgent):
    """Analyzes numerical data"""
    
    def __init__(self):
        super().__init__(
            name="Numerical Agent",
            description="Analyzes numerical data and statistics"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Analyze numerical data"""
        
        numeric_cols = columns if columns else self._get_numeric_columns(df)
        
        if not numeric_cols:
            return {'message': 'No numerical columns found'}
        
        # Calculate statistics
        stats_dict = DataAnalyzer.calculate_numerical_stats(df, numeric_cols)
        
        # Calculate correlation
        correlation = DataAnalyzer.calculate_correlation(df, numeric_cols)
        
        # Identify high correlations
        high_correlations = self._identify_high_correlations(correlation)
        
        # Distribution analysis
        distributions = self._analyze_distributions(df, numeric_cols)
        
        return {
            'statistics': stats_dict,
            'correlation': correlation,
            'high_correlations': high_correlations,
            'distributions': distributions,
            'visualization_data': self._prepare_visualization_data(df, numeric_cols, stats_dict),
        }
    
    def _identify_high_correlations(self, correlation: Dict) -> list:
        """Identify highly correlated column pairs"""
        high_corrs = []
        
        # Convert to numeric for comparison
        corr_dict = correlation
        for col1 in corr_dict:
            for col2 in corr_dict[col1]:
                if col1 != col2:
                    corr_value = corr_dict[col1][col2]
                    if abs(corr_value) > 0.7:
                        high_corrs.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': corr_value,
                        })
        
        return high_corrs
    
    def _analyze_distributions(self, df: pd.DataFrame, numeric_cols: list) -> Dict[str, str]:
        """Analyze distribution shapes"""
        distributions = {}
        
        for col in numeric_cols:
            data = df[col].dropna()
            skewness = float(pd.Series(data).skew())
            
            if abs(skewness) < 0.5:
                dist = 'symmetric'
            elif skewness > 0:
                dist = 'right_skewed'
            else:
                dist = 'left_skewed'
            
            distributions[col] = dist
        
        return distributions
    
    def _prepare_visualization_data(self, df: pd.DataFrame, numeric_cols: list, 
                                     stats_dict: Dict) -> Dict[str, Any]:
        """Prepare data for visualizations"""
        
        viz_data = {
            'histograms': {},
            'boxplots': {},
        }
        
        for col in numeric_cols[:5]:  # Limit to first 5 for performance
            data = df[col].dropna()
            
            # Histogram data
            hist, bins = np.histogram(data, bins=20)
            viz_data['histograms'][col] = {
                'values': hist.tolist(),
                'bins': bins.tolist(),
            }
            
            # Boxplot data
            viz_data['boxplots'][col] = {
                'min': float(data.min()),
                'q1': float(data.quantile(0.25)),
                'median': float(data.median()),
                'q3': float(data.quantile(0.75)),
                'max': float(data.max()),
            }
        
        return viz_data
