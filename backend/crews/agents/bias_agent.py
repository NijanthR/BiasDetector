"""
Bias Agent - Detects bias in datasets
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import BiasDetector, DataAnalyzer
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class BiasAgent(BaseAnalysisAgent):
    """Detects bias in datasets"""
    
    def __init__(self):
        super().__init__(
            name="Bias Detection Agent",
            description="Detects and analyzes bias in datasets"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Detect bias in dataset"""
        
        bias_analysis = {
            'overall_bias_score': 0,
            'biased_columns': [],
            'bias_metrics': {},
            'fairness_report': {},
        }
        
        categorical_cols = self._get_categorical_columns(df)
        
        # Analyze bias for each categorical column
        for col in categorical_cols:
            bias_metrics = BiasDetector.calculate_bias_metrics(df, col)
            bias_analysis['bias_metrics'][col] = bias_metrics
            
            # If highly biased, add to flagged columns
            if bias_metrics['bias_score'] > 30:
                bias_analysis['biased_columns'].append({
                    'column': col,
                    'bias_score': bias_metrics['bias_score'],
                    'balance_status': bias_metrics['balance_status'],
                })
        
        # Calculate overall bias score
        if bias_analysis['bias_metrics']:
            bias_scores = [m['bias_score'] for m in bias_analysis['bias_metrics'].values()]
            bias_analysis['overall_bias_score'] = np.mean(bias_scores)
        
        # Generate fairness report
        bias_analysis['fairness_report'] = self._generate_fairness_report(df, bias_analysis)
        
        return bias_analysis
    
    def _generate_fairness_report(self, df: pd.DataFrame, bias_analysis: Dict) -> Dict[str, Any]:
        """Generate fairness and bias report"""
        
        report = {
            'summary': "",
            'recommendations': [],
            'critical_findings': [],
        }
        
        if bias_analysis['overall_bias_score'] > 60:
            report['summary'] = "Dataset shows significant bias. Immediate action recommended."
            report['critical_findings'].append("High overall bias detected in the dataset")
        elif bias_analysis['overall_bias_score'] > 30:
            report['summary'] = "Dataset shows moderate bias. Review recommended."
            report['critical_findings'].append("Moderate bias levels detected")
        else:
            report['summary'] = "Dataset appears relatively balanced"
        
        # Add specific recommendations
        if len(bias_analysis['biased_columns']) > 0:
            for col_info in bias_analysis['biased_columns']:
                if col_info['bias_score'] > 60:
                    report['recommendations'].append(
                        f"Column '{col_info['column']}' is highly biased. "
                        f"Consider rebalancing or using weighted sampling."
                    )
        
        return report
