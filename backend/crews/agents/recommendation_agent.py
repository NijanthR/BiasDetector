"""
Recommendation Agent - Generates recommendations for data improvement
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import DataAnalyzer
from typing import Dict, Any, Optional
import pandas as pd


class RecommendationAgent(BaseAnalysisAgent):
    """Generates recommendations for data improvement"""
    
    def __init__(self):
        super().__init__(
            name="Recommendation Agent",
            description="Generates recommendations for data improvement"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Generate recommendations"""
        
        recommendations = {
            'data_cleaning': [],
            'preprocessing': [],
            'model_recommendations': [],
            'improvement_suggestions': [],
            'priority_actions': [],
        }
        
        # Analyze and generate recommendations
        quality_metrics = DataAnalyzer.calculate_quality_metrics(df)
        
        # Data cleaning recommendations
        recommendations['data_cleaning'] = self._get_cleaning_recommendations(df, quality_metrics)
        
        # Preprocessing recommendations
        recommendations['preprocessing'] = self._get_preprocessing_recommendations(df)
        
        # Model recommendations
        recommendations['model_recommendations'] = self._get_model_recommendations(df)
        
        # General improvements
        recommendations['improvement_suggestions'] = self._get_improvement_suggestions(df, quality_metrics)
        
        # Priority actions
        recommendations['priority_actions'] = self._prioritize_actions(recommendations)
        
        return recommendations
    
    def _get_cleaning_recommendations(self, df: pd.DataFrame, quality_metrics: Dict) -> list:
        """Get data cleaning recommendations"""
        
        recommendations = []
        
        # Missing values
        if quality_metrics['missing_percentage'] > 5:
            recommendations.append({
                'action': 'Handle Missing Values',
                'severity': 'high' if quality_metrics['missing_percentage'] > 20 else 'medium',
                'details': f"Missing value ratio: {quality_metrics['missing_percentage']}%",
                'options': ['Imputation', 'Deletion', 'Forward/Backward fill (for time series)']
            })
        
        # Duplicates
        if quality_metrics['duplicate_percentage'] > 1:
            recommendations.append({
                'action': 'Remove Duplicate Records',
                'severity': 'high' if quality_metrics['duplicate_percentage'] > 5 else 'medium',
                'details': f"Duplicate records: {quality_metrics['duplicate_rows']}",
                'options': ['Remove all duplicates', 'Keep first occurrence', 'Manual review']
            })
        
        return recommendations
    
    def _get_preprocessing_recommendations(self, df: pd.DataFrame) -> list:
        """Get preprocessing recommendations"""
        
        recommendations = []
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        
        # Normalization
        if numeric_cols:
            recommendations.append({
                'action': 'Normalize/Standardize Numerical Features',
                'severity': 'medium',
                'details': f"Numeric columns: {len(numeric_cols)}",
                'options': ['Min-Max Scaling', 'Z-score Normalization', 'Log Transformation']
            })
        
        # Encoding
        if categorical_cols:
            recommendations.append({
                'action': 'Encode Categorical Features',
                'severity': 'high',
                'details': f"Categorical columns: {len(categorical_cols)}",
                'options': ['One-Hot Encoding', 'Label Encoding', 'Binary Encoding']
            })
        
        # Feature scaling
        if numeric_cols and len(numeric_cols) > 1:
            recommendations.append({
                'action': 'Scale Features to Similar Range',
                'severity': 'low',
                'details': 'Features may have different scales',
                'options': ['Standardization', 'Normalization']
            })
        
        return recommendations
    
    def _get_model_recommendations(self, df: pd.DataFrame) -> list:
        """Get model recommendations based on data"""
        
        recommendations = []
        numeric_cols = self._get_numeric_columns(df)
        
        # Determine problem type
        if any('price' in col.lower() or 'amount' in col.lower() or 'value' in col.lower() 
               for col in df.columns):
            recommendations.append({
                'model_type': 'Regression',
                'suitable_models': [
                    'Linear Regression',
                    'Random Forest Regressor',
                    'Gradient Boosting',
                    'XGBoost'
                ]
            })
        else:
            recommendations.append({
                'model_type': 'Classification',
                'suitable_models': [
                    'Logistic Regression',
                    'Random Forest',
                    'SVM',
                    'Gradient Boosting'
                ]
            })
        
        return recommendations
    
    def _get_improvement_suggestions(self, df: pd.DataFrame, quality_metrics: Dict) -> list:
        """Get general improvement suggestions"""
        
        suggestions = []
        
        # Feature engineering
        suggestions.append({
            'suggestion': 'Perform Feature Engineering',
            'reason': 'Create new features from existing ones',
            'examples': ['Polynomial features', 'Interaction features', 'Time-based features']
        })
        
        # Data balance
        suggestions.append({
            'suggestion': 'Address Class Imbalance (if applicable)',
            'reason': 'Improves model performance on imbalanced datasets',
            'examples': ['Over-sampling', 'Under-sampling', 'SMOTE']
        })
        
        # Outlier handling
        suggestions.append({
            'suggestion': 'Review and Handle Outliers',
            'reason': 'Outliers can skew model training',
            'examples': ['Z-score method', 'IQR method', 'Statistical bounds']
        })
        
        return suggestions
    
    def _prioritize_actions(self, recommendations: Dict) -> list:
        """Prioritize actions by importance"""
        
        actions = []
        
        # Add high priority items
        for action in recommendations.get('data_cleaning', []):
            if action.get('severity') == 'high':
                actions.append({
                    'priority': 'critical',
                    'action': action['action'],
                    'reason': action['details']
                })
        
        # Add medium priority items
        for action in recommendations.get('data_cleaning', []):
            if action.get('severity') == 'medium':
                actions.append({
                    'priority': 'high',
                    'action': action['action'],
                    'reason': action['details']
                })
        
        # Add preprocessing
        for action in recommendations.get('preprocessing', [])[:2]:
            actions.append({
                'priority': 'high',
                'action': action['action'],
                'reason': action['details']
            })
        
        return actions
