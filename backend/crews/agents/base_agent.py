"""
Base agent class for dataset analysis
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAnalysisAgent(ABC):
    """Base class for all analysis agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.start_time = None
        self.end_time = None
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        """Initialize the Groq model for agent use"""
        try:
            from langchain_groq import ChatGroq
            api_key = os.getenv("GROQ_API_KEY")
            if api_key and api_key != "your_api_key_here":
                model_name = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
                model_name = model_name.replace("groq/", "")
                return ChatGroq(
                    model=model_name,
                    groq_api_key=api_key,
                    temperature=0.2
                )
        except ImportError:
            print("Warning: langchain-groq is not installed.")
        return None
    
    @abstractmethod
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """
        Analyze dataset
        
        Args:
            df: DataFrame to analyze
            columns: Specific columns to analyze (optional)
        
        Returns:
            Dictionary with analysis results
        """
        pass
    
    def execute(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Execute analysis with timing"""
        try:
            self.start_time = datetime.now()
            result = self.analyze(df, columns)
            self.end_time = datetime.now()
            
            execution_time = (self.end_time - self.start_time).total_seconds()
            
            return {
                'status': 'success',
                'agent': self.name,
                'timestamp': self.end_time.isoformat(),
                'execution_time': execution_time,
                'data': result,
            }
        except Exception as e:
            return {
                'status': 'error',
                'agent': self.name,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
            }
    
    def _get_numeric_columns(self, df: pd.DataFrame) -> list:
        """Get numeric columns from DataFrame"""
        return df.select_dtypes(include=['float64', 'float32', 'int64', 'int32']).columns.tolist()
    
    def _get_categorical_columns(self, df: pd.DataFrame) -> list:
        """Get categorical columns from DataFrame"""
        return df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def _get_datetime_columns(self, df: pd.DataFrame) -> list:
        """Get datetime columns from DataFrame"""
        return df.select_dtypes(include=['datetime64']).columns.tolist()
