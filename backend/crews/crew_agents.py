import os
from crewai import Agent, LLM
from dotenv import load_dotenv

load_dotenv(override=True)

def get_llm():
    """Get LLM instance using Groq"""
    model = os.getenv("LLM_MODEL", "groq/openai/gpt-oss-120b")
    if not model.startswith("groq/"):
        model = f"groq/{model}"
    return LLM(
        model=model,
        api_key=os.getenv("GROQ_API_KEY")
    )

llm = get_llm()

dataset_analyzer = Agent(
    role="Dataset Analyzer",
    goal="Analyze datasets to uncover insights, calculate quality metrics, and extract meaning.",
    backstory="You are an expert data analyst. You excel at looking at datasets and finding the core insights, quality issues, and summary statistics.",
    llm=llm,
    verbose=True
)

classifier = Agent(
    role="Classifier",
    goal="Classify the type and structure of the dataset.",
    backstory="You are an expert data engineer who quickly understands the schema, data types, and primary classification of any dataset (e.g., numerical, time_series, text).",
    llm=llm,
    verbose=True
)

bias_detector = Agent(
    role="Bias Detector",
    goal="Detect biases and imbalances in the dataset.",
    backstory="You are an AI ethicist and statistician. You are highly skilled at spotting class imbalances, unrepresented groups, and statistical biases in datasets.",
    llm=llm,
    verbose=True
)

recommendation_agent = Agent(
    role="Data Consultant",
    goal="Provide actionable recommendations for improving dataset quality and modeling approach.",
    backstory="You are a senior data consultant. You advise data science teams on the best preprocessing steps, cleaning strategies, and model selection.",
    llm=llm,
    verbose=True
)

report_agent = Agent(
    role="Report Writer",
    goal="Summarize all analysis findings into a cohesive, executive-level report.",
    backstory="You are a technical writer and data translator. You take complex statistical findings and summarize them into clear, actionable executive reports.",
    llm=llm,
    verbose=True
)
