"""
Mixed Data Agent - Analyzes relationships across mixed data types
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import DataAnalyzer
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class MixedDataAgent(BaseAnalysisAgent):
    """Analyzes relationships in mixed data"""
    
    def __init__(self):
        super().__init__(
            name="Mixed Data Agent",
            description="Analyzes relationships across mixed data types"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Analyze mixed data relationships"""
        
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        
        analysis_results = {
            'feature_interactions': {},
            'cross_type_analysis': {},
            'encoding_suggestions': {},
            'feature_importance': {},
        }
        
        # Analyze numeric-categorical relationships
        if numeric_cols and categorical_cols:
            for cat_col in categorical_cols[:5]:
                for num_col in numeric_cols[:5]:
                    interaction_key = f"{cat_col}_vs_{num_col}"
                    analysis_results['feature_interactions'][interaction_key] = \
                        self._analyze_interaction(df, cat_col, num_col)
        
        # Encoding suggestions
        analysis_results['encoding_suggestions'] = self._suggest_encodings(df, categorical_cols)
        
        # Feature importance based on variance
        analysis_results['feature_importance'] = self._calculate_feature_importance(df)
        
        return analysis_results
    
    def _analyze_interaction(self, df: pd.DataFrame, cat_col: str, num_col: str) -> Dict[str, Any]:
        """Analyze interaction between categorical and numerical columns"""
        
        interaction = {}
        
        # Group numeric by categorical
        grouped = df.groupby(cat_col)[num_col].agg(['mean', 'std', 'count'])
        
        interaction['by_category'] = grouped.to_dict()
        
        # Check if relationship is significant
        try:
            from scipy.stats import f_oneway
            groups = [group[num_col].values for name, group in df.groupby(cat_col)]
            f_stat, p_value = f_oneway(*groups)
            
            interaction['correlation_strength'] = 'strong' if p_value < 0.05 else 'weak'
            interaction['p_value'] = float(p_value)
        except:
            interaction['correlation_strength'] = 'unknown'
        
        return interaction
    
    def _suggest_encodings(self, df: pd.DataFrame, categorical_cols: list) -> Dict[str, str]:
        """Suggest encoding strategies for categorical columns"""
        
        suggestions = {}
        
        for col in categorical_cols:
            unique_count = df[col].nunique()
            
            if unique_count <= 2:
                suggestions[col] = 'binary_encoding'
            elif unique_count <= 10:
                suggestions[col] = 'one_hot_encoding'
            else:
                suggestions[col] = 'label_encoding'
        
        return suggestions
    
    def _calculate_feature_importance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate feature importance based on variance"""
        
        importance = {}
        numeric_cols = self._get_numeric_columns(df)
        
        # Normalize variance for comparison
        variances = df[numeric_cols].var()
        total_variance = variances.sum()
        
        for col in numeric_cols:
            importance[col] = float(variances[col] / total_variance * 100) if total_variance > 0 else 0
        
        # Sort by importance
        importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        
        return importance
