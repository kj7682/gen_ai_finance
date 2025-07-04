import pandas as pd
import os

class ExcelReportParser:
    def __init__(self, excel_filepath):
        if not os.path.exists(excel_filepath):
            raise FileNotFoundError(f"Error: Excel file not found at {excel_filepath}")
        self.excel_filepath = excel_filepath
        self.data_sheets = {} # To store loaded DataFrames

    def load_sheet(self, sheet_name=None):
        """
        Loads a specific sheet or the first sheet if sheet_name is None.
        Stores the loaded DataFrame in self.data_sheets.
        """
        try:
            if sheet_name:
                df = pd.read_excel(self.excel_filepath, sheet_name=sheet_name)
                self.data_sheets[sheet_name] = df
                print(f"Sheet '{sheet_name}' loaded successfully.")
            else:
                # Load the first sheet by default
                xls = pd.ExcelFile(self.excel_filepath)
                first_sheet_name = xls.sheet_names[0]
                df = xls.parse(first_sheet_name)
                self.data_sheets[first_sheet_name] = df
                print(f"First sheet '{first_sheet_name}' loaded successfully.")
                return first_sheet_name # Return the name of the loaded sheet
            return sheet_name
        except Exception as e:
            print(f"Error loading sheet '{sheet_name if sheet_name else 'first sheet'}': {e}")
            return None

    def get_metrics_as_dataframe(self, sheet_name, metrics_to_extract, metric_column_name="Financial Metric"):
        """
        Extracts specified metrics and returns them as a pandas DataFrame suitable for trend analysis.
        Metrics will be rows, periods will be columns.

        Args:
            sheet_name (str): The name of the sheet to process (must be loaded first).
            metrics_to_extract (list): A list of strings, where each string is a metric to find.
            metric_column_name (str): The name of the column that contains the metric labels/names.

        Returns:
            pd.DataFrame: DataFrame with metrics as index and periods as columns.
                          Returns None if sheet not found or other errors.
        """
        if sheet_name not in self.data_sheets:
            print(f"Error: Sheet '{sheet_name}' not loaded. Please load it first.")
            return None

        df_orig = self.data_sheets[sheet_name]

        if metric_column_name not in df_orig.columns:
            print(f"Error: Metric column '{metric_column_name}' not found in sheet '{sheet_name}'.")
            return None

        # Filter for the metrics we want and set the metric column as index
        metrics_df = df_orig[df_orig[metric_column_name].isin(metrics_to_extract)].copy()
        if metrics_df.empty:
            print(f"Warning: None of the specified metrics found in sheet '{sheet_name}'.")
            return pd.DataFrame() # Return empty DataFrame

        metrics_df.set_index(metric_column_name, inplace=True)

        # Ensure all values are numeric, converting if necessary
        for col in metrics_df.columns:
            metrics_df[col] = pd.to_numeric(metrics_df[col], errors='coerce')

        # Reindex to ensure the order of metrics is as requested and all requested metrics are present
        metrics_df = metrics_df.reindex(metrics_to_extract)

        # Attempt to sort columns by period (assuming 'YYYY-QX' format)
        # This is a bit naive, more robust parsing might be needed for complex period names
        try:
            sorted_columns = sorted(metrics_df.columns, key=lambda x: (x.split('-')[0], x.split('-')[1]))
            metrics_df = metrics_df[sorted_columns]
        except Exception as e:
            print(f"Warning: Could not sort period columns. Using original order. Error: {e}")

        return metrics_df

    def calculate_period_over_period_change(self, metrics_df):
        """
        Calculates the percentage change between consecutive periods for each metric.

        Args:
            metrics_df (pd.DataFrame): DataFrame with metrics as index and periods as columns.

        Returns:
            pd.DataFrame: DataFrame with percentage changes. First period column will be NaN.
        """
        if not isinstance(metrics_df, pd.DataFrame) or metrics_df.empty:
            print("Error: Input is not a valid DataFrame or is empty.")
            return pd.DataFrame()

        # Ensure values are numeric for pct_change
        # This should ideally be handled when creating metrics_df, but as a safeguard:
        numeric_df = metrics_df.apply(pd.to_numeric, errors='coerce')

        # Calculate percentage change along columns (axis=1)
        # .T transposes so periods are rows, then pct_change, then .T back
        trend_df = numeric_df.T.pct_change(fill_method=None).T * 100

        # The first period column will have NaNs after pct_change, which is expected.
        return trend_df


if __name__ == "__main__":
    sample_file_path = "sample_healthcare_financials.xlsx"

    # Adjust path if running from /app directory
    if os.getcwd() == "/app" and not os.path.exists(sample_file_path):
        potential_path = os.path.join("financial_report_analyzer", sample_file_path)
        if os.path.exists(potential_path):
            sample_file_path = potential_path
        else:
            print(f"Test Error: Sample file '{sample_file_path}' or '{potential_path}' not found.")
            exit()
    elif not os.path.exists(sample_file_path):
         print(f"Test Error: Sample file '{sample_file_path}' not found in CWD ({os.getcwd()}).")
         exit()

    parser = ExcelReportParser(sample_file_path)
    loaded_sheet_name = parser.load_sheet() # Default sheet is "Financials_And_Stats"

    if loaded_sheet_name:
        defined_metrics = [
            'Total Patient Revenue',
            'Total Operating Revenue',
            'Total Operating Expenses',
            'Net Operating Income',
            'Net Income (Loss)',
            'Number of Beds',
            'Patient Days',
            'Average Length of Stay (Days)',
            'Occupancy Rate (%)',
            'Emergency Room Visits',
            'NonExistentMetric' # Test for missing metric handling
        ]

        print(f"\nExtracting metrics as DataFrame from sheet: '{loaded_sheet_name}'")
        metrics_dataframe = parser.get_metrics_as_dataframe(loaded_sheet_name, defined_metrics)

        if metrics_dataframe is not None and not metrics_dataframe.empty:
            print("\nExtracted Metrics DataFrame:")
            print(metrics_dataframe)

            pop_change_dataframe = parser.calculate_period_over_period_change(metrics_dataframe)
            if pop_change_dataframe is not None and not pop_change_dataframe.empty:
                print("\nCalculating Period-over-Period Change (%):")
                print(pop_change_dataframe)

                # Integrate TrendAnalyzer
                from trend_analyzer import TrendAnalyzer # Assuming it's in the same directory

                analyzer = TrendAnalyzer(metrics_dataframe, pop_change_dataframe)

                print("\n--- Advanced Trend Analysis Summary (Structured) ---")
                structured_summary = analyzer.generate_text_summary(
                    metrics_to_analyze=metrics_dataframe.index.tolist(),
                    streak_min_length=1 # Use 1 for more sensitivity in demo
                )
                print(structured_summary)

                # Integrate LLM Summarizer
                from llm_summarizer import generate_llm_prompt, get_simulated_llm_summary

                print("\n--- LLM Integration ---")
                # Assuming the company name can be generic for now, or extracted from filename/sheet if available
                company_name_for_llm = "the organization"
                excel_filename = os.path.basename(sample_file_path)
                if "sample_healthcare_financials" in excel_filename.lower(): # Basic heuristic
                    company_name_for_llm = "Sample Healthcare Org"

                llm_prompt = generate_llm_prompt(structured_summary, company_name=company_name_for_llm)
                # print("\nGenerated LLM Prompt (for debugging):")
                # print(llm_prompt)

                narrative_summary = get_simulated_llm_summary(llm_prompt)
                print("\n--- Simulated LLM Narrative Summary ---")
                print(narrative_summary)

            else:
                print("Could not calculate period-over-period changes.")

        elif metrics_dataframe is not None and metrics_dataframe.empty:
             print("Metrics DataFrame is empty (e.g. no metrics found or sheet was empty).")
        else:
            print("Failed to extract metrics as DataFrame (the DataFrame is None).")
    else:
        print("Could not load any sheet from the Excel file.")
