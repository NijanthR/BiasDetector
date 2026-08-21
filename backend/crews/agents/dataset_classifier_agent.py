"""
Dataset Classifier Agent - Classifies dataset type and structure
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import DataAnalyzer
from typing import Dict, Any, Optional
import pandas as pd


class DatasetClassifierAgent(BaseAnalysisAgent):
    """Classifies dataset type and extracts schema information"""
    
    def __init__(self):
        super().__init__(
            name="Dataset Classifier",
            description="Classifies dataset type and structure"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Classify dataset and extract schema"""
        
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        datetime_cols = self._get_datetime_columns(df)
        
        # Detect column types
        column_types = DataAnalyzer.detect_column_types(df)
        
        # Determine primary dataset type
        dataset_type = self._determine_dataset_type(df, numeric_cols, categorical_cols, datetime_cols)
        
        schema = {
            'columns': {
                col: {
                    'type': column_types.get(col, 'unknown'),
                    'dtype': str(df[col].dtype),
                    'non_null_count': int(df[col].notna().sum()),
                    'null_count': int(df[col].isna().sum()),
                    'unique_values': int(df[col].nunique()),
                }
                for col in df.columns
            },
            'numeric_columns': numeric_cols,
            'categorical_columns': categorical_cols,
            'datetime_columns': datetime_cols,
            'shape': {
                'rows': df.shape[0],
                'columns': df.shape[1],
            },
        }
        
        return {
            'dataset_type': dataset_type,
            'schema': schema,
            'column_types': column_types,
            'numeric_count': len(numeric_cols),
            'categorical_count': len(categorical_cols),
            'datetime_count': len(datetime_cols),
        }
    
    def _determine_dataset_type(self, df: pd.DataFrame, numeric_cols: list, 
                                categorical_cols: list, datetime_cols: list) -> str:
        """Determine the primary dataset type"""
        
        # Check for time series
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            return 'time_series'
        
        # Check for transaction data (has datetime and amounts)
        if len(datetime_cols) > 0 and len(numeric_cols) > 0:
            # Check for transaction-like columns
            transaction_keywords = ['amount', 'price', 'quantity', 'transaction', 'order', 'payment']
            col_names_lower = [col.lower() for col in df.columns]
            if any(keyword in ' '.join(col_names_lower) for keyword in transaction_keywords):
                return 'transaction'
        
        # Check for sentiment/text data
        if len(categorical_cols) > 0 and len(numeric_cols) == 0:
            # Check for text columns with high cardinality
            for col in categorical_cols:
                if df[col].nunique() > df.shape[0] * 0.5:
                    return 'sentiment'
        
        # Determine mixed vs single type
        total_cols = len(numeric_cols) + len(categorical_cols)
        numeric_ratio = len(numeric_cols) / total_cols if total_cols > 0 else 0
        
        if 0.3 < numeric_ratio < 0.7:
            return 'mixed'
        elif numeric_ratio > 0.7:
            return 'numerical'
        elif numeric_ratio < 0.3:
            return 'categorical'
        else:
            return 'mixed'
