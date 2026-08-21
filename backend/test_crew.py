"""
Test script for AgentOrchestrator
"""
import pandas as pd
from database import init_db
from crews.orchestrator import AgentOrchestrator

def test_orchestrator():
    print("Initializing database...")
    init_db()

    print("Creating sample dataframe...")
    df = pd.DataFrame({
        'age': [25, 30, 35, 40, 45],
        'salary': [50000, 60000, 70000, 80000, 90000],
        'department': ['IT', 'HR', 'IT', 'Sales', 'HR']
    })
    
    print("Running AgentOrchestrator...")
    orchestrator = AgentOrchestrator()
    try:
        results = orchestrator.orchestrate(df)
        print("Success!")
        print("Keys:", results.keys())
    except Exception as e:
        print("Error occurred!")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_orchestrator()
