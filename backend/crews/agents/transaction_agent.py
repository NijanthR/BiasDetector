"""
Transaction Agent - Analyzes transaction/financial data
"""
from .base_agent import BaseAnalysisAgent
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class TransactionAgent(BaseAnalysisAgent):
    """Analyzes transaction and financial data"""
    
    def __init__(self):
        super().__init__(
            name="Transaction Agent",
            description="Analyzes transaction and financial data"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Analyze transaction data"""
        
        analysis_results = {
            'transaction_summary': {},
            'fraud_indicators': {},
            'revenue_analysis': {},
            'customer_analysis': {},
        }
        
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        datetime_cols = self._get_datetime_columns(df)
        
        # Transaction summary
        amount_col = self._find_amount_column(numeric_cols)
        if amount_col:
            analysis_results['transaction_summary'] = {
                'total_transactions': len(df),
                'total_revenue': float(df[amount_col].sum()),
                'average_transaction': float(df[amount_col].mean()),
                'min_transaction': float(df[amount_col].min()),
                'max_transaction': float(df[amount_col].max()),
                'std_dev': float(df[amount_col].std()),
            }
        
        # Fraud detection indicators
        analysis_results['fraud_indicators'] = self._detect_fraud_indicators(df, numeric_cols)
        
        # Revenue analysis
        if datetime_cols and amount_col:
            analysis_results['revenue_analysis'] = self._analyze_revenue_trends(
                df, datetime_cols[0], amount_col
            )
        
        # Customer segmentation
        if categorical_cols:
            analysis_results['customer_analysis'] = self._analyze_customers(df, numeric_cols)
        
        return analysis_results
    
    def _find_amount_column(self, numeric_cols: list) -> Optional[str]:
        """Find the amount/transaction value column"""
        keywords = ['amount', 'price', 'value', 'total', 'revenue', 'sales']
        
        for col in numeric_cols:
            if any(keyword in col.lower() for keyword in keywords):
                return col
        
        # Return first numeric column if no match
        return numeric_cols[0] if numeric_cols else None
    
    def _detect_fraud_indicators(self, df: pd.DataFrame, numeric_cols: list) -> Dict[str, Any]:
        """Detect potential fraud indicators"""
        
        indicators = {
            'suspicious_patterns': [],
            'high_value_transactions': 0,
            'outlier_transactions': 0,
            'risk_score': 0,
        }
        
        amount_col = self._find_amount_column(numeric_cols)
        if not amount_col:
            return indicators
        
        amounts = df[amount_col]
        
        # Calculate statistics
        mean = amounts.mean()
        std = amounts.std()
        
        # High value transactions (> mean + 2*std)
        high_value = amounts[amounts > (mean + 2 * std)]
        indicators['high_value_transactions'] = len(high_value)
        
        # Outliers
        Q1 = amounts.quantile(0.25)
        Q3 = amounts.quantile(0.75)
        IQR = Q3 - Q1
        
        outliers = amounts[(amounts < Q1 - 1.5*IQR) | (amounts > Q3 + 1.5*IQR)]
        indicators['outlier_transactions'] = len(outliers)
        
        # Risk score
        if len(high_value) > len(df) * 0.1:
            indicators['suspicious_patterns'].append("High number of large transactions")
            indicators['risk_score'] += 20
        
        if len(outliers) > len(df) * 0.05:
            indicators['suspicious_patterns'].append("Multiple outlier values detected")
            indicators['risk_score'] += 15
        
        return indicators
    
    def _analyze_revenue_trends(self, df: pd.DataFrame, date_col: str, amount_col: str) -> Dict[str, Any]:
        """Analyze revenue trends over time"""
        
        df_sorted = df.sort_values(date_col)
        df_sorted[date_col] = pd.to_datetime(df_sorted[date_col])
        
        # Group by date
        daily_revenue = df_sorted.groupby(df_sorted[date_col].dt.date)[amount_col].sum()
        
        return {
            'daily_average': float(daily_revenue.mean()),
            'daily_min': float(daily_revenue.min()),
            'daily_max': float(daily_revenue.max()),
            'trend': 'increasing' if daily_revenue.iloc[-1] > daily_revenue.iloc[0] else 'decreasing',
        }
    
    def _analyze_customers(self, df: pd.DataFrame, numeric_cols: list) -> Dict[str, Any]:
        """Analyze customer patterns"""
        
        customer_analysis = {
            'unique_customers': 0,
            'avg_customer_value': 0,
            'top_customers': 0,
        }
        
        # Check for customer column
        customer_col = None
        for col in df.columns:
            if 'customer' in col.lower() or 'client' in col.lower() or 'id' in col.lower():
                customer_col = col
                break
        
        if customer_col:
            customer_analysis['unique_customers'] = df[customer_col].nunique()
            
            # Find amount column for customer value
            amount_col = self._find_amount_column(numeric_cols)
            if amount_col:
                customer_values = df.groupby(customer_col)[amount_col].sum()
                customer_analysis['avg_customer_value'] = float(customer_values.mean())
                customer_analysis['top_customers'] = int(customer_values.nlargest(10).sum())
        
        return customer_analysis
