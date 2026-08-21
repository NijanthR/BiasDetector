"""
Debug: Upload a dataset and print full error traceback
"""
import os
import sys
import traceback
import pandas as pd
from database import SessionLocal
from models import Dataset
from crews.orchestrator import AgentOrchestrator

with SessionLocal() as db:
    d = db.query(Dataset).order_by(Dataset.uploaded_at.desc()).first()
    if not d:
        print("No datasets found in database.")
        sys.exit(0)

    print(f"Testing with: {d.name}, status={d.analysis_status}")
    file_path = d.file
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)

    if d.file_type == 'csv':
        df = pd.read_csv(file_path)
    elif d.file_type == 'xlsx':
        df = pd.read_excel(file_path)
    else:
        df = pd.read_json(file_path)

    print(f"Loaded {df.shape[0]} rows x {df.shape[1]} cols")

    try:
        orch = AgentOrchestrator()
        results = orch.orchestrate(df, dataset=d)
        print("SUCCESS:", list(results.keys()))
    except Exception as e:
        print("FAILED WITH:")
        traceback.print_exc()
