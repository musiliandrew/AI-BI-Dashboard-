import pandas as pd

def preprocess_and_analyze(file_path):
    df = pd.read_csv(file_path)
    summary = df.describe()  # Basic statistical summary
    return summary.to_json()
