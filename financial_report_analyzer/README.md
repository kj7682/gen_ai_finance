# Financial Report Trend Analyzer

## Overview

This tool analyzes financial reports provided in Excel format to identify key trends and generate analytical summaries. It extracts financial metrics, calculates period-over-period changes, performs advanced trend analysis (like identifying growth/decline streaks and deviations from average), and provides both a structured textual summary and a simulated natural language narrative of the findings.

It is designed with a focus on healthcare industry metrics but can be adapted for other types of financial data.

## Features

*   **Excel Data Parsing:** Loads financial data from `.xlsx` files using `pandas`.
*   **Metric Extraction:** Identifies and extracts predefined financial and operational metrics.
*   **Period-over-Period (PoP) Change:** Calculates percentage changes between consecutive periods for all metrics.
*   **Advanced Trend Analysis:**
    *   **Consecutive Streaks:** Detects consistent growth or decline over multiple periods.
    *   **Metric Averages:** Calculates the average for each metric across all periods.
    *   **Deviation Analysis:** Highlights significant deviations of metric values from their averages.
*   **Structured Summary:** Generates a detailed textual report of all analyses performed.
*   **Simulated LLM Narrative:** Produces a high-level, conversational summary simulating the output of a Large Language Model based on the structured analysis.

## Project Structure

The tool is organized into several Python modules:

*   `sample_healthcare_financials.xlsx`: A sample Excel file containing mock healthcare financial data used for demonstration and testing.
*   `excel_generator.py`: A utility script to generate the `sample_healthcare_financials.xlsx` file.
*   `report_parser.py`: The main script for parsing the Excel report. It orchestrates the analysis flow, utilizing other modules for detailed trend analysis and summarization. This is the primary execution point.
*   `trend_analyzer.py`: Contains the `TrendAnalyzer` class, which performs advanced trend calculations (streaks, averages, deviations) on the data extracted by `report_parser.py`.
*   `llm_summarizer.py`: Includes functions to generate a prompt from the structured trend analysis and a *simulated* LLM function to create a narrative summary.

## Setup & Dependencies

### Prerequisites

*   Python 3 (developed with Python 3.12, but should be compatible with recent Python 3 versions)

### Libraries

The project relies on the following Python libraries:

*   `pandas`
*   `numpy` (as a dependency of pandas)
*   `openpyxl` (for reading `.xlsx` files with pandas)

You can install these dependencies using pip. It's recommended to use a virtual environment.

```bash
# (Optional, but recommended) Create and activate a virtual environment
# python -m venv venv
# source venv/bin/activate  # On Linux/macOS
# .\venv\Scripts\activate    # On Windows

pip install pandas openpyxl
```
Alternatively, if a `requirements.txt` file is provided:
```bash
pip install -r requirements.txt
```

## How to Run

1.  Ensure all dependencies are installed.
2.  Make sure the `sample_healthcare_financials.xlsx` file is present in the `financial_report_analyzer` directory. If not, you can generate it by running:
    ```bash
    python excel_generator.py
    ```
    (If running from the parent directory of `financial_report_analyzer`, use `python financial_report_analyzer/excel_generator.py`)

3.  To run the full analysis pipeline, execute the `report_parser.py` script:
    ```bash
    python report_parser.py
    ```
    (If running from the parent directory, use `python financial_report_analyzer/report_parser.py`)

## Sample Output

When `report_parser.py` is run, it will print several pieces of information to the console:

1.  **Extracted Metrics DataFrame:** A table showing the key financial metrics and their values for each period.
2.  **Period-over-Period Change (%):** A table showing the percentage change for each metric from one period to the next.
3.  **Advanced Trend Analysis Summary (Structured):** A detailed textual breakdown including:
    *   Average values for each metric.
    *   Descriptions of consecutive growth/decline streaks.
    *   Notes on significant deviations from the average for each metric.
4.  **Simulated LLM Narrative Summary:** A paragraph-style summary that mimics how an LLM might describe the key findings. This output will explicitly state it's a simulation.

## LLM Integration Note

The current LLM summarization feature is a *simulation*. The `llm_summarizer.py` module uses rule-based logic and template filling to generate a narrative. It does **not** make any calls to external LLM APIs.

To integrate a real LLM (like OpenAI's GPT, Google's Gemini, or an open-source model):
1.  Modify `llm_summarizer.py`.
2.  Replace the `get_simulated_llm_summary` function's internal logic with actual API calls to your chosen LLM service.
3.  You would need to handle API keys, request formatting, and response parsing according to the LLM provider's SDK or API documentation.
4.  Ensure the environment where this code runs has network access and necessary credentials for the LLM API.
