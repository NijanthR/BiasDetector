"""
Backfill script for updating keywords on existing reports
"""
import os
import pandas as pd
from database import SessionLocal
from models import Report
from crews.tools.data_tools import TextAnalyzer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with SessionLocal() as db:
    reports = db.query(Report).all()
    for r in reports:
        dataset = r.dataset
        if not dataset:
            continue
        try:
            file_path = dataset.file
            if not os.path.isabs(file_path):
                file_path = os.path.join(BASE_DIR, file_path)

            df = pd.read_csv(file_path) if dataset.file_type == 'csv' else pd.read_excel(file_path) if dataset.file_type == 'xlsx' else pd.read_json(file_path)

            sentiment_col = next((c for c in df.columns if 'sentiment' in c.lower()), None) or next((c for c in df.columns if 'label' in c.lower() or 'rating' in c.lower()), None)
            text_col = next((c for c in df.columns if ('text' in c.lower() or 'comment' in c.lower() or 'desc' in c.lower() or 'msg' in c.lower() or 'review' in c.lower()) and 'id' not in c.lower()), None)

            if not text_col or not sentiment_col:
                continue

            pos_mask = df[sentiment_col].astype(str).str.contains('pos|5|4', case=False, na=False)
            neg_mask = df[sentiment_col].astype(str).str.contains('neg|1|2|0', case=False, na=False)

            pos_texts = df[pos_mask][text_col].dropna().tolist()
            neg_texts = df[neg_mask][text_col].dropna().tolist()

            pos_words = TextAnalyzer.extract_keywords(pos_texts, top_n=10)
            neg_words = TextAnalyzer.extract_keywords(neg_texts, top_n=10)

            sm = dict(r.summary or {})
            sm['top_positive_words'] = list(pos_words.keys())
            sm['top_negative_words'] = list(neg_words.keys())
            r.summary = sm
            db.commit()
            print(f"Updated words for {r.title}")
        except Exception as e:
            print(f"Skipped {r.title}: {e}")
