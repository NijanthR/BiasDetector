"""
Cleaning Agent - Suggests data cleaning operations
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import DataAnalyzer
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class CleaningAgent(BaseAnalysisAgent):
    """Suggests data cleaning operations"""
    
    def __init__(self):
        super().__init__(
            name="Cleaning Agent",
            description="Suggests data cleaning operations"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Suggest cleaning operations"""
        
        cleaning_suggestions = {
            'missing_value_strategies': {},
            'duplicate_handling': {},
            'outlier_handling': {},
            'data_type_issues': {},
            'standardization_suggestions': {},
        }
        
        # Missing value strategies
        cleaning_suggestions['missing_value_strategies'] = self._suggest_missing_value_handling(df)
        
        # Duplicate handling
        cleaning_suggestions['duplicate_handling'] = self._suggest_duplicate_handling(df)
        
        # Outlier handling
        numeric_cols = self._get_numeric_columns(df)
        for col in numeric_cols[:5]:
            cleaning_suggestions['outlier_handling'][col] = self._suggest_outlier_handling(df[col])
        
        # Data type issues
        cleaning_suggestions['data_type_issues'] = self._identify_data_type_issues(df)
        
        # Standardization
        cleaning_suggestions['standardization_suggestions'] = self._suggest_standardization(df)
        
        return cleaning_suggestions
    
    def _suggest_missing_value_handling(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Suggest strategies for handling missing values"""
        
        strategies = {}
        
        for col in df.columns:
            missing_pct = (df[col].isna().sum() / len(df)) * 100
            
            if missing_pct > 0:
                if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                    strategy = {
                        'column': col,
                        'missing_percentage': missing_pct,
                        'suggested_methods': [
                            'Mean Imputation',
                            'Median Imputation',
                            'KNN Imputation',
                            'Deletion (if < 5% missing)',
                        ],
                        'recommendation': 'Mean/Median imputation' if missing_pct < 30 else 'Consider deletion'
                    }
                else:
                    strategy = {
                        'column': col,
                        'missing_percentage': missing_pct,
                        'suggested_methods': [
                            'Mode Imputation',
                            'Forward Fill (for time series)',
                            'Deletion',
                            'Create "Unknown" category',
                        ],
                        'recommendation': 'Mode imputation or category' if missing_pct < 30 else 'Consider deletion'
                    }
                
                strategies[col] = strategy
        
        return strategies
    
    def _suggest_duplicate_handling(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Suggest strategies for handling duplicates"""
        
        duplicates = df.duplicated().sum()
        duplicate_pct = (duplicates / len(df)) * 100
        
        return {
            'duplicate_count': int(duplicates),
            'duplicate_percentage': float(duplicate_pct),
            'suggested_methods': [
                'Remove all duplicates',
                'Keep first occurrence',
                'Keep last occurrence',
                'Manual review of duplicates'
            ],
            'recommendation': 'Remove all duplicates' if duplicate_pct > 1 else 'No action needed'
        }
    
    def _suggest_outlier_handling(self, series: pd.Series) -> Dict[str, Any]:
        """Suggest strategies for handling outliers"""
        
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        outliers = series[(series < Q1 - 1.5*IQR) | (series > Q3 + 1.5*IQR)]
        outlier_pct = (len(outliers) / len(series)) * 100
        
        return {
            'outlier_count': len(outliers),
            'outlier_percentage': float(outlier_pct),
            'suggested_methods': [
                'Remove outliers',
                'Cap at IQR boundaries',
                'Transform (log, sqrt)',
                'Keep as is if legitimate'
            ],
            'recommendation': 'Cap outliers' if outlier_pct < 5 else 'Review and handle appropriately'
        }
    
    def _identify_data_type_issues(self, df: pd.DataFrame) -> Dict[str, list]:
        """Identify data type inconsistencies"""
        
        issues = {}
        
        for col in df.columns:
            col_issues = []
            
            # Check for mixed types in object columns
            if df[col].dtype == 'object':
                non_null_values = df[col].dropna()
                types = set(type(val) for val in non_null_values)
                
                if len(types) > 1:
                    col_issues.append(f"Mixed types detected: {types}")
            
            if col_issues:
                issues[col] = col_issues
        
        return issues
    
    def _suggest_standardization(self, df: pd.DataFrame) -> Dict[str, str]:
        """Suggest standardization methods"""
        
        suggestions = {}
        
        # Text standardization
        for col in df.columns:
            if df[col].dtype == 'object':
                suggestions[col] = 'Text standardization: lowercase, trim whitespace, remove special characters'
        
        # Numeric standardization
        numeric_cols = self._get_numeric_columns(df)
        for col in numeric_cols:
            suggestions[col] = 'Numeric standardization: handle decimals, validate ranges, check units'
        
        return suggestions
