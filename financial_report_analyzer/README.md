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

## Sample Output Description

When `report_parser.py` is run, it will print several pieces of information to the console:

1.  **Extracted Metrics DataFrame:** A table showing the key financial metrics and their values for each period.
2.  **Period-over-Period Change (%):** A table showing the percentage change for each metric from one period to the next.
3.  **Structured Trend Analysis:** A detailed textual breakdown including:
    *   Average values for each metric.
    *   Descriptions of consecutive growth/decline streaks.
    *   Notes on significant deviations from the average for each metric.
4.  **Simulated LLM Narrative Summary:** A paragraph-style summary that mimics how an LLM might describe the key findings. This output will explicitly state it's a simulation.

(See the "Example Console Output" section below for an actual truncated sample.)

## LLM Integration Note

The current LLM summarization feature is a *simulation*. The `llm_summarizer.py` module uses rule-based logic and template filling to generate a narrative. It does **not** make any calls to external LLM APIs.

To integrate a real LLM (like OpenAI's GPT, Google's Gemini, or an open-source model):
1.  Modify `llm_summarizer.py`.
2.  Replace the `get_simulated_llm_summary` function's internal logic with actual API calls to your chosen LLM service.
3.  You would need to handle API keys, request formatting, and response parsing according to the LLM provider's SDK or API documentation.
4.  Ensure the environment where this code runs has network access and necessary credentials for the LLM API.

## Example Console Output

Below is a sample of the output generated when running `python financial_report_analyzer/report_parser.py`:

```text
First sheet 'Financials_And_Stats' loaded successfully.

Extracting metrics as DataFrame from sheet: 'Financials_And_Stats'

Extracted Metrics DataFrame:
                                   2023-Q4     2024-Q1     2024-Q2
Financial Metric
Total Patient Revenue          10000000.00  10200000.0  10500000.0
Total Operating Revenue        10500000.00  10710000.0  11020000.0
Total Operating Expenses        7500000.00   7665000.0   7830000.0
Net Operating Income            3000000.00   3045000.0   3190000.0
Net Income (Loss)               3150000.00   3203000.0   3355000.0
Number of Beds                      200.00       200.0       205.0
Patient Days                      15000.00     15300.0     15800.0
Average Length of Stay (Days)         7.50         7.6         7.7
Occupancy Rate (%)                   81.52        85.0        84.7
Emergency Room Visits              5000.00      5100.0      5250.0
NonExistentMetric                      NaN         NaN         NaN

Calculating Period-over-Period Change (%):
                               2023-Q4   2024-Q1   2024-Q2
Financial Metric
Total Patient Revenue              NaN  2.000000  2.941176
Total Operating Revenue            NaN  2.000000  2.894491
Total Operating Expenses           NaN  2.200000  2.152642
Net Operating Income               NaN  1.500000  4.761905
Net Income (Loss)                  NaN  1.682540  4.745551
Number of Beds                     NaN  0.000000  2.500000
Patient Days                       NaN  2.000000  3.267974
Average Length of Stay (Days)      NaN  1.333333  1.315789
Occupancy Rate (%)                 NaN  4.268891 -0.352941
Emergency Room Visits              NaN  2.000000  2.941176
NonExistentMetric                  NaN       NaN       NaN

--- Structured Trend Analysis ---
Trend Analysis Summary:

Metric Averages:
  - Total Patient Revenue: 10,233,333.33
  - Total Operating Revenue: 10,743,333.33
  - Total Operating Expenses: 7,665,000.00
  - Net Operating Income: 3,078,333.33
  - Net Income (Loss): 3,236,000.00
  - Number of Beds: 201.67
  - Patient Days: 15,366.67
  - Average Length of Stay (Days): 7.60
  - Occupancy Rate (%): 83.74
  - Emergency Room Visits: 5,116.67
  - NonExistentMetric: nan


Analysis for Metric: Total Patient Revenue
  - Consecutive Growth: 2 periods, from 2023-Q4 (10,000,000.00) to 2024-Q2 (10,500,000.00). Change first noted in 2024-Q1.

Analysis for Metric: Total Operating Revenue
  - Consecutive Growth: 2 periods, from 2023-Q4 (10,500,000.00) to 2024-Q2 (11,020,000.00). Change first noted in 2024-Q1.

Analysis for Metric: Total Operating Expenses
  - Consecutive Growth: 2 periods, from 2023-Q4 (7,500,000.00) to 2024-Q2 (7,830,000.00). Change first noted in 2024-Q1.

Analysis for Metric: Net Operating Income
  - Consecutive Growth: 2 periods, from 2023-Q4 (3,000,000.00) to 2024-Q2 (3,190,000.00). Change first noted in 2024-Q1.

Analysis for Metric: Net Income (Loss)
  - Consecutive Growth: 2 periods, from 2023-Q4 (3,150,000.00) to 2024-Q2 (3,355,000.00). Change first noted in 2024-Q1.

Analysis for Metric: Number of Beds
  - Consecutive Growth: 1 periods, from 2024-Q1 (200.00) to 2024-Q2 (205.00). Change first noted in 2024-Q2.

Analysis for Metric: Patient Days
  - Consecutive Growth: 2 periods, from 2023-Q4 (15,000.00) to 2024-Q2 (15,800.00). Change first noted in 2024-Q1.

Analysis for Metric: Average Length of Stay (Days)
  - Consecutive Growth: 2 periods, from 2023-Q4 (7.50) to 2024-Q2 (7.70). Change first noted in 2024-Q1.

Analysis for Metric: Occupancy Rate (%)
  - Consecutive Growth: 1 periods, from 2023-Q4 (81.52) to 2024-Q1 (85.00). Change first noted in 2024-Q1.
  - Consecutive Decline: 1 periods, from 2024-Q1 (85.00) to 2024-Q2 (84.70). Change first noted in 2024-Q2.

Analysis for Metric: Emergency Room Visits
  - Consecutive Growth: 2 periods, from 2023-Q4 (5,000.00) to 2024-Q2 (5,250.00). Change first noted in 2024-Q1.

Analysis for Metric: NonExistentMetric


--- LLM Integration ---

--- Simulated LLM Narrative Summary ---
--- Simulated LLM Narrative Summary (Illustrative) ---

Overall, the financial report for the organization indicates several noteworthy trends. Profitability appears to be improving. Key operational metrics such as Patient Days, Occupancy Rate, Emergency Room Visits also showed some activity.

It is advisable to look deeper into these areas to understand the underlying drivers. (Note: This is a simulated summary based on structured data.)
```
