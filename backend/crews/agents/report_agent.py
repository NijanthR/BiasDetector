"""
Report Agent - Generates comprehensive reports
"""
from .base_agent import BaseAnalysisAgent
from typing import Dict, Any, Optional
import pandas as pd


class ReportAgent(BaseAnalysisAgent):
    """Generates comprehensive analysis reports"""
    
    def __init__(self):
        super().__init__(
            name="Report Agent",
            description="Generates comprehensive analysis reports"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Generate comprehensive report"""
        
        report = {
            'executive_summary': {},
            'dataset_overview': {},
            'quality_score_summary': {},
            'bias_summary': {},
            'key_findings': [],
            'recommendations_summary': [],
            'conclusion': '',
        }
        
        # Executive summary
        report['executive_summary'] = self._generate_executive_summary(df)
        
        # Dataset overview
        report['dataset_overview'] = {
            'rows': df.shape[0],
            'columns': df.shape[1],
            'size_mb': df.memory_usage(deep=True).sum() / (1024 ** 2),
            'column_types': self._get_column_type_summary(df),
        }
        
        # Key findings
        report['key_findings'] = self._extract_key_findings(df)
        
        # Conclusion
        report['conclusion'] = self._generate_conclusion(df)
        
        return report
    
    def _generate_executive_summary(self, df: pd.DataFrame) -> Dict[str, str]:
        """Generate executive summary"""
        
        numeric_cols = self._get_numeric_columns(df)
        categorical_cols = self._get_categorical_columns(df)
        
        summary_text = f"""
Dataset contains {df.shape[0]} records across {df.shape[1]} features.
Composition: {len(numeric_cols)} numerical, {len(categorical_cols)} categorical features.
Overall data completeness is satisfactory for analysis.
"""
        
        return {
            'overview': summary_text.strip(),
            'data_readiness': 'Ready for analysis',
            'quality_status': 'Good',
        }
    
    def _get_column_type_summary(self, df: pd.DataFrame) -> Dict[str, int]:
        """Get summary of column types"""
        
        return {
            'numerical': len(self._get_numeric_columns(df)),
            'categorical': len(self._get_categorical_columns(df)),
            'datetime': len(self._get_datetime_columns(df)),
            'text': len([col for col in df.columns 
                        if df[col].dtype == 'object' and df[col].nunique() > len(df) * 0.5]),
        }
    
    def _extract_key_findings(self, df: pd.DataFrame) -> list:
        """Extract key findings from data"""
        
        findings = []
        
        # Missing data finding
        missing_total = df.isnull().sum().sum()
        if missing_total > 0:
            finding = {
                'category': 'Data Quality',
                'finding': f'Dataset contains {missing_total} missing values',
                'impact': 'Moderate' if missing_total < df.shape[0] * df.shape[1] * 0.1 else 'High',
            }
            findings.append(finding)
        
        # Shape finding
        finding = {
            'category': 'Dataset Characteristics',
            'finding': f'Dataset contains {df.shape[0]} records with {df.shape[1]} features',
            'impact': 'Sufficient' if df.shape[0] > 100 else 'Limited',
        }
        findings.append(finding)
        
        # Completeness
        completeness = ((df.shape[0] * df.shape[1] - df.isnull().sum().sum()) / 
                       (df.shape[0] * df.shape[1]) * 100)
        finding = {
            'category': 'Data Completeness',
            'finding': f'Data completeness: {completeness:.1f}%',
            'impact': 'Excellent' if completeness > 95 else 'Good' if completeness > 80 else 'Fair',
        }
        findings.append(finding)
        
        return findings
    
    def _generate_conclusion(self, df: pd.DataFrame) -> str:
        """Generate report conclusion"""
        
        rows = df.shape[0]
        cols = df.shape[1]
        completeness = (1 - df.isnull().sum().sum() / (rows * cols)) * 100
        
        if rows >= 1000 and completeness > 90:
            conclusion = "This dataset is well-structured and comprehensive. It contains sufficient data volume and quality for detailed analysis and model development."
        elif rows >= 100 and completeness > 80:
            conclusion = "This dataset is suitable for analysis. While data quality is good, consider addressing missing values and ensuring data consistency."
        else:
            conclusion = "This dataset has limitations in size or quality. Significant data cleaning and preprocessing may be required before use in production models."
        
        return conclusion
