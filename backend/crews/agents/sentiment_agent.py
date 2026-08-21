"""
Sentiment Agent - Analyzes text and sentiment data
"""
from .base_agent import BaseAnalysisAgent
from ..tools.data_tools import TextAnalyzer
from typing import Dict, Any, Optional
import pandas as pd
from textblob import TextBlob
from collections import Counter


class SentimentAgent(BaseAnalysisAgent):
    """Analyzes text and sentiment data"""
    
    def __init__(self):
        super().__init__(
            name="Sentiment Agent",
            description="Analyzes text and sentiment data"
        )
    
    def analyze(self, df: pd.DataFrame, columns: Optional[list] = None) -> Dict[str, Any]:
        """Analyze sentiment and text data"""
        
        text_cols = columns if columns else self._identify_text_columns(df)
        
        if not text_cols:
            return {'message': 'No text columns found'}
        
        analysis_results = {
            'text_statistics': {},
            'sentiment_analysis': {},
            'keywords': {},
        }
        
        for col in text_cols:
            texts = df[col].astype(str).tolist()
            
            # Text statistics
            analysis_results['text_statistics'][col] = TextAnalyzer.get_text_statistics(texts)
            
            # Sentiment analysis
            analysis_results['sentiment_analysis'][col] = self._analyze_sentiment(texts)
            
            # Keywords extraction
            analysis_results['keywords'][col] = TextAnalyzer.extract_keywords(texts, top_n=10)
        
        return analysis_results
    
    def _identify_text_columns(self, df: pd.DataFrame) -> list:
        """Identify text/string columns"""
        return [col for col in df.columns if df[col].dtype == 'object']
    
    def _analyze_sentiment(self, texts: list) -> Dict[str, Any]:
        """Analyze sentiment of texts"""
        
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        polarities = []
        subjectivities = []
        
        for text in texts:
            if pd.notna(text) and len(str(text).strip()) > 0:
                try:
                    blob = TextBlob(str(text))
                    polarity = blob.sentiment.polarity
                    subjectivity = blob.sentiment.subjectivity
                    
                    polarities.append(polarity)
                    subjectivities.append(subjectivity)
                    
                    if polarity > 0.1:
                        sentiments['positive'] += 1
                    elif polarity < -0.1:
                        sentiments['negative'] += 1
                    else:
                        sentiments['neutral'] += 1
                except:
                    sentiments['neutral'] += 1
        
        total = sum(sentiments.values())
        
        return {
            'distribution': {
                'positive': sentiments['positive'],
                'negative': sentiments['negative'],
                'neutral': sentiments['neutral'],
            },
            'percentages': {
                'positive': round((sentiments['positive'] / total * 100), 2) if total > 0 else 0,
                'negative': round((sentiments['negative'] / total * 100), 2) if total > 0 else 0,
                'neutral': round((sentiments['neutral'] / total * 100), 2) if total > 0 else 0,
            },
            'average_polarity': round(sum(polarities) / len(polarities), 3) if polarities else 0,
            'average_subjectivity': round(sum(subjectivities) / len(subjectivities), 3) if subjectivities else 0,
        }
