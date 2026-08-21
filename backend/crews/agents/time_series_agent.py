"""
Time Series Agent - Analyzes time series data
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import TimeSeriesAnalyzer
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class TimeSeriesAgent(BaseAnalysisAgent):
    """Analyzes time series data"""
    
    def __init__(self):
        super().__init__(
            name="Time Series Agent",
            description="Analyzes time series data"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Analyze time series data"""
        
        datetime_cols = self._get_datetime_columns(df)
        numeric_cols = self._get_numeric_columns(df)
        
        if not datetime_cols or not numeric_cols:
            return {'message': 'No time series data found (need datetime and numeric columns)'}
        
        # Sort by datetime
        date_col = datetime_cols[0]
        df_sorted = df.sort_values(date_col)
        
        analysis_results = {
            'trend_analysis': {},
            'seasonality_analysis': {},
            'anomalies': {},
            'forecast_readiness': {},
        }
        
        for col in numeric_cols[:5]:  # Analyze first 5 numeric columns
            series = df_sorted[col].dropna()
            
            if len(series) < 3:
                continue
            
            # Trend analysis
            analysis_results['trend_analysis'][col] = TimeSeriesAnalyzer.detect_trend(series)
            
            # Seasonality analysis
            analysis_results['seasonality_analysis'][col] = TimeSeriesAnalyzer.detect_seasonality(series)
            
            # Anomaly detection
            analysis_results['anomalies'][col] = self._detect_anomalies(series)
            
            # Forecast readiness
            analysis_results['forecast_readiness'][col] = self._assess_forecast_readiness(series)
        
        # Time range
        analysis_results['time_range'] = {
            'start': str(df_sorted[date_col].min()),
            'end': str(df_sorted[date_col].max()),
            'duration_days': int((df_sorted[date_col].max() - df_sorted[date_col].min()).days),
        }
        
        return analysis_results
    
    def _detect_anomalies(self, series: pd.Series) -> Dict[str, Any]:
        """Detect anomalies using IQR method"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            'anomaly_count': len(anomalies),
            'anomaly_percentage': round((len(anomalies) / len(series)) * 100, 2),
            'lower_bound': float(lower_bound),
            'upper_bound': float(upper_bound),
        }
    
    def _assess_forecast_readiness(self, series: pd.Series) -> Dict[str, Any]:
        """Assess readiness for forecasting"""
        
        # Check stationarity using Augmented Dickey-Fuller test
        try:
            from statsmodels.tsa.stattools import adfuller
            adf_result = adfuller(series.dropna())
            is_stationary = adf_result[1] < 0.05
        except:
            is_stationary = False
        
        readiness_score = 0
        issues = []
        
        # Check minimum length
        if len(series) >= 30:
            readiness_score += 20
        else:
            issues.append("Insufficient data points (need at least 30)")
        
        # Check missing values
        missing_pct = (series.isna().sum() / len(series)) * 100
        if missing_pct < 10:
            readiness_score += 20
        else:
            issues.append(f"Too many missing values ({missing_pct}%)")
        
        # Check stationarity
        if is_stationary:
            readiness_score += 20
        else:
            issues.append("Data is not stationary")
        
        # Check variance
        if series.std() > 0:
            readiness_score += 20
        else:
            issues.append("No variance in data")
        
        readiness_score += 20  # Base score
        
        return {
            'forecast_readiness_score': min(100, readiness_score),
            'is_stationary': is_stationary,
            'issues': issues,
            'recommendation': 'Ready for forecasting' if readiness_score >= 80 else 'Not ready for forecasting',
        }
