
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "httpx",
#   "chardet",
#   "python-dotenv",
# ]
# ///

import os
import sys
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import httpx
import chardet
from dotenv import load_dotenv

# Force non-interactive matplotlib backend
matplotlib.use('Agg')

# Load environment variables
load_dotenv()

# Constants
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

if not AIPROXY_TOKEN:
    raise ValueError("API token not set. Please set AIPROXY_TOKEN in the environment.")

def load_data(file_path):
    """Load CSV data with encoding detection."""
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        return pd.read_csv(file_path, encoding=encoding)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

def analyze_data(df):
    """Perform basic data analysis."""
    numeric_df = df.select_dtypes(include=['number'])  # Select only numeric columns
    analysis = {
        'summary': df.describe(include='all').to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'correlation': numeric_df.corr().to_dict()  # Compute correlation only on numeric columns
    }
    return analysis

def visualize_data(df, output_dir):
    """Generate and save visualizations."""
    sns.set(style="whitegrid")
    numeric_columns = df.select_dtypes(include=['number']).columns
    for column in numeric_columns:
        plt.figure()
        sns.histplot(df[column].dropna(), kde=True)
        plt.title(f'Distribution of {column}')
        plt.savefig(os.path.join(output_dir, f'{column}_distribution.png'))
        plt.close()

def generate_narrative(analysis):
    """Generate narrative using LLM."""
    headers = {
        'Authorization': f'Bearer {AIPROXY_TOKEN}',
        'Content-Type': 'application/json'
    }
    prompt = f"Provide a detailed analysis based on the following data summary: {analysis}"
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = httpx.post(API_URL, headers=headers, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return "Narrative generation failed due to an error."

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze datasets and generate insights.")
    parser.add_argument("file_path", help="Path to the dataset CSV file.")
    parser.add_argument("-o", "--output_dir", default="output", help="Directory to save outputs.")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Load data
    df = load_data(args.file_path)

    # Analyze data
    analysis = analyze_data(df)

    # Visualize data
    visualize_data(df, args.output_dir)

    # Generate narrative
    narrative = generate_narrative(analysis)

    # Save narrative
    with open(os.path.join(args.output_dir, 'README.md'), 'w') as f:
        f.write(narrative)

if __name__ == "__main__":
    main()
=======
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "seaborn",
#   "pandas",
#   "matplotlib",
#   "httpx",
#   "chardet",
#   "numpy",
#   "openai"
# ]
# ///
import pandas as pd
import openai
import matplotlib
matplotlib.use("Agg")  # Use a non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys

def get_token():
    """Prompt the user to enter the AIPROXY token."""
    token = input("Enter your AIPROXY token: ").strip()
    if not token:
        raise ValueError("AIPROXY token is required to proceed.")
    return token


def create_correlation_heatmap(data):
    """Creates a correlation heatmap and saves it to a file."""
    numeric_data = data.select_dtypes(include=['number'])
    if numeric_data.empty:
        print("No numeric data available for correlation heatmap.")
        return None

    corr_matrix = numeric_data.corr()
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
    plt.title("Correlation Heatmap")
    filename = "correlation_heatmap.png"
    plt.savefig(filename)
    plt.close()
    return filename

def create_boxplot(data):
    """Creates a boxplot for outlier detection and saves it to a file."""
    numeric_data = data.select_dtypes(include=['number'])
    if numeric_data.empty:
        print("No numeric data available for boxplot.")
        return None

    plt.figure(figsize=(12, 6))
    sns.boxplot(data=numeric_data)
    plt.title("Boxplot for Outlier Detection")
    filename = "boxplot.png"
    plt.savefig(filename)
    plt.close()
    return filename

def perform_clustering(data, n_clusters=3):
    """Performs KMeans clustering and saves the cluster plot to a file."""
    from sklearn.cluster import KMeans
    import numpy as np

    numeric_data = data.select_dtypes(include=[np.number]).dropna()
    if numeric_data.shape[1] < 2:
        print("Not enough numeric columns for clustering.")
        return None

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(numeric_data)

    plt.figure(figsize=(8, 6))
    plt.scatter(numeric_data.iloc[:, 0], numeric_data.iloc[:, 1], c=clusters, cmap="viridis")
    plt.title("Cluster Analysis")
    plt.xlabel(numeric_data.columns[0])
    plt.ylabel(numeric_data.columns[1])
    filename = "clusters.png"
    plt.savefig(filename)
    plt.close()
    return filename

# Process the dataset
def process_dataset(csv_file, token):
    print(f"Processing {csv_file}...")

    try:
        # Try reading the dataset with different encodings
        data = pd.read_csv(csv_file, encoding='ISO-8859-1')
    except UnicodeDecodeError:
        print(f"Error: Unable to read {csv_file} due to encoding issues.")
        return
    except FileNotFoundError:
        print(f"Error: File {csv_file} not found.")
        return

    print(data.columns)
    print(data.head())

    summary = data.describe(include="all")
    print(summary)

    missing_data = data.isnull().sum()
    print(missing_data)

    # AI Analysis - Generate summary for the CSV file
    report_prompt = f"""
    Create a summary of the dataset {csv_file}. Include:
    - Overview of key statistics
    - Top trends or correlations
    - Recommendations for next steps
    """

    openai.api_key = token
    openai.api_base = "https://aiproxy.sanand.workers.dev/openai/v1"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[ 
                {"role": "system", "content": "You are an assistant generating data analysis summaries."},
                {"role": "user", "content": report_prompt}
            ],
            max_tokens=300
        )
    except Exception as e:
        print(f"Error communicating with the AI: {e}")
        return

    report_text = response['choices'][0]['message']['content'].strip()

    # Save the report
    report_filename = f"{os.path.splitext(csv_file)[0]}_README.md"
    with open(report_filename, "w") as f:
        f.write(f"# Data Analysis Report for {csv_file.capitalize()}\n")
        f.write("## Summary\n")
        f.write(report_text + "\n\n")

    # Generate visualizations
    charts = []
    heatmap_file = create_correlation_heatmap(data)
    if heatmap_file:
        charts.append(heatmap_file)

    boxplot_file = create_boxplot(data)
    if boxplot_file:
        charts.append(boxplot_file)

    clusters_file = perform_clustering(data, n_clusters=3)
    if clusters_file:
        charts.append(clusters_file)

    print(f"Generated charts: {charts}")

    print(f"Finished processing {csv_file}. Results saved for {csv_file}.")

def main():
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py <dataset.csv>")
        sys.exit(1)

    csv_file = sys.argv[1]
    token = get_token()
    process_dataset(csv_file, token)

if __name__ == "__main__":
    main()

