"""
Data analysis and processing tools for agents
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import stats
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')


class DataAnalyzer:
    """Utility class for data analysis"""
    
    @staticmethod
    def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
        """Detect data types for each column"""
        column_types = {}
        
        for col in df.columns:
            if df[col].dtype in ['int64', 'int32', 'int16', 'int8']:
                column_types[col] = 'INT'
            elif df[col].dtype in ['float64', 'float32']:
                column_types[col] = 'FLOAT'
            elif df[col].dtype == 'datetime64[ns]':
                column_types[col] = 'DATE'
            elif df[col].dtype == 'bool':
                column_types[col] = 'BOOLEAN'
            else:
                column_types[col] = 'STRING'
        
        return column_types
    
    @staticmethod
    def calculate_quality_metrics(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        duplicates = df.duplicated().sum()
        
        metrics = {
            'total_rows': df.shape[0],
            'total_columns': df.shape[1],
            'total_cells': total_cells,
            'missing_cells': missing_cells,
            'missing_percentage': round((missing_cells / total_cells) * 100, 2),
            'duplicate_rows': duplicates,
            'duplicate_percentage': round((duplicates / df.shape[0]) * 100, 2) if df.shape[0] > 0 else 0,
            'completeness': round(100 - (missing_cells / total_cells) * 100, 2),
            'column_missing': df.isnull().sum().to_dict(),
        }
        
        return metrics
    
    @staticmethod
    def detect_outliers(data: pd.Series) -> Dict[str, Any]:
        """Detect outliers using IQR method"""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        
        return {
            'outlier_count': len(outliers),
            'outlier_percentage': round((len(outliers) / len(data)) * 100, 2),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
            'IQR': float(IQR),
        }
    
    @staticmethod
    def calculate_numerical_stats(df: pd.DataFrame, columns: List[str]) -> Dict[str, Dict]:
        """Calculate statistics for numerical columns"""
        stats_dict = {}
        
        for col in columns:
            if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                data = df[col].dropna()
                
                stats_dict[col] = {
                    'mean': float(data.mean()),
                    'median': float(data.median()),
                    'mode': float(data.mode().iloc[0]) if len(data.mode()) > 0 else None,
                    'std_dev': float(data.std()),
                    'variance': float(data.var()),
                    'min': float(data.min()),
                    'max': float(data.max()),
                    'q1': float(data.quantile(0.25)),
                    'q3': float(data.quantile(0.75)),
                    'skewness': float(stats.skew(data)),
                    'kurtosis': float(stats.kurtosis(data)),
                    'count': int(len(data)),
                }
                
                # Add outlier detection
                stats_dict[col]['outliers'] = DataAnalyzer.detect_outliers(data)
        
        return stats_dict
    
    @staticmethod
    def calculate_correlation(df: pd.DataFrame, numerical_cols: List[str]) -> Dict[str, Dict]:
        """Calculate correlation matrix for numerical columns"""
        if len(numerical_cols) < 2:
            return {}
        
        numeric_df = df[numerical_cols].select_dtypes(include=[np.number])
        corr_matrix = numeric_df.corr()
        
        return corr_matrix.to_dict()
    
    @staticmethod
    def detect_class_imbalance(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Detect class imbalance in categorical column"""
        value_counts = df[column].value_counts()
        total = len(df)
        
        imbalance = {
            'unique_values': len(value_counts),
            'distribution': (value_counts / total * 100).to_dict(),
            'max_class': str(value_counts.idxmax()),
            'max_class_percentage': float(value_counts.max() / total * 100),
            'min_class': str(value_counts.idxmin()),
            'min_class_percentage': float(value_counts.min() / total * 100),
            'imbalance_ratio': float(value_counts.max() / value_counts.min()) if value_counts.min() > 0 else 0,
        }
        
        return imbalance
    
    @staticmethod
    def calculate_entropy(df: pd.DataFrame, column: str) -> float:
        """Calculate Shannon entropy for categorical column"""
        value_counts = df[column].value_counts()
        probabilities = value_counts / len(df)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return float(entropy)


class TextAnalyzer:
    """Utility class for text analysis"""
    
    @staticmethod
    def get_text_statistics(texts: List[str]) -> Dict[str, Any]:
        """Calculate statistics for text data"""
        lengths = [len(str(t).split()) for t in texts if pd.notna(t)]
        
        stats = {
            'avg_words': float(np.mean(lengths)) if lengths else 0,
            'max_words': int(np.max(lengths)) if lengths else 0,
            'min_words': int(np.min(lengths)) if lengths else 0,
            'total_texts': len(texts),
            'empty_texts': sum(1 for t in texts if pd.isna(t) or len(str(t).strip()) == 0),
        }
        
        return stats
    
    @staticmethod
    def extract_keywords(texts: List[str], top_n: int = 10) -> Dict[str, int]:
        """Extract top keywords from texts"""
        from collections import Counter
        
        words = []
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'to', 'for', 'of', 'in', 'and', 'or', 'not'}
        
        for text in texts:
            if pd.notna(text):
                text_words = str(text).lower().split()
                words.extend([w for w in text_words if w not in stop_words and len(w) > 2])
        
        return dict(Counter(words).most_common(top_n))


class TimeSeriesAnalyzer:
    """Utility class for time series analysis"""
    
    @staticmethod
    def detect_trend(series: pd.Series) -> Dict[str, Any]:
        """Detect trend in time series"""
        x = np.arange(len(series))
        y = series.values
        
        # Remove NaN values
        mask = ~np.isnan(y)
        x = x[mask]
        y = y[mask]
        
        if len(x) < 2:
            return {'trend': 'insufficient_data', 'slope': 0}
        
        z = np.polyfit(x, y, 1)
        slope = float(z[0])
        
        trend = 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'flat'
        
        return {
            'trend': trend,
            'slope': slope,
            'mean_value': float(np.nanmean(y)),
            'std_dev': float(np.nanstd(y)),
        }
    
    @staticmethod
    def detect_seasonality(series: pd.Series) -> Dict[str, Any]:
        """Detect seasonality in time series"""
        if len(series) < 7:
            return {'has_seasonality': False, 'period': None}
        
        # Simple seasonal decomposition
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        try:
            result = seasonal_decompose(series.dropna(), model='additive', period=min(12, len(series)//2))
            seasonal_strength = np.var(result.seasonal) / np.var(result.observed) if np.var(result.observed) > 0 else 0
            
            return {
                'has_seasonality': seasonal_strength > 0.1,
                'seasonal_strength': float(seasonal_strength),
                'period': int(min(12, len(series)//2)),
            }
        except:
            return {'has_seasonality': False, 'period': None}


class BiasDetector:
    """Utility class for bias detection"""
    
    @staticmethod
    def detect_bias_distribution(df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Detect bias in distribution"""
        value_counts = df[column].value_counts()
        total = len(df)
        percentages = (value_counts / total * 100).round(2)
        
        # Calculate bias metrics
        max_percentage = percentages.max()
        min_percentage = percentages.min()
        mean_percentage = 100 / len(value_counts)
        
        bias_score = min(max_percentage - mean_percentage, 100)
        
        return {
            'distribution': percentages.to_dict(),
            'bias_score': float(bias_score),
            'most_dominant_class': {
                'class': str(value_counts.idxmax()),
                'percentage': float(max_percentage),
            },
            'least_represented_class': {
                'class': str(value_counts.idxmin()),
                'percentage': float(min_percentage),
            },
            'expected_percentage': float(mean_percentage),
        }
    
    @staticmethod
    def calculate_bias_metrics(df: pd.DataFrame, target_column: str) -> Dict[str, Any]:
        """Calculate comprehensive bias metrics"""
        if target_column not in df.columns:
            return {'error': 'Column not found'}
        
        value_counts = df[target_column].value_counts()
        total = len(df)
        
        # Calculate entropy
        probabilities = value_counts / total
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Normalized entropy (0 = maximum bias, 1 = maximum balance)
        max_entropy = np.log2(len(value_counts))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        # Bias score (inverse of normalized entropy)
        bias_score = (1 - normalized_entropy) * 100
        
        return {
            'entropy': float(entropy),
            'normalized_entropy': float(normalized_entropy),
            'bias_score': float(bias_score),
            'class_distribution': value_counts.to_dict(),
            'balance_status': 'balanced' if normalized_entropy > 0.7 else 'moderately_biased' if normalized_entropy > 0.3 else 'highly_biased',
        }
