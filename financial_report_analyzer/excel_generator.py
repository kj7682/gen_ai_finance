import pandas as pd
import os

def create_sample_excel(filepath="sample_healthcare_financials.xlsx"):
    """
    Creates a sample Excel file with mock healthcare financial data.
    """
    data = {
        'Financial Metric': [
            'Total Patient Revenue', 'Other Operating Revenue', 'Total Operating Revenue',
            'Salaries and Wages', 'Medical Supplies', 'Depreciation and Amortization',
            'Interest Expense', 'Other Operating Expenses', 'Total Operating Expenses',
            'Net Operating Income',
            'Non-Operating Revenue', 'Non-Operating Expenses', 'Net Non-Operating Income/Loss',
            'Net Income (Loss)',
            None, # For blank row
            'Key Statistics',
            'Number of Beds', 'Patient Days', 'Average Length of Stay (Days)', 'Occupancy Rate (%)',
            'Emergency Room Visits'
        ],
        '2023-Q4': [
            10000000, 500000, 10500000,
            4000000, 1500000, 700000,
            300000, 1000000, 7500000,
            3000000,
            200000, 50000, 150000,
            3150000,
            None,
            None,
            200, 15000, 7.5, 0, # Placeholder for Occupancy Rate
            5000
        ],
        '2024-Q1': [
            10200000, 510000, 10710000,
            4050000, 1550000, 710000,
            305000, 1050000, 0, # Placeholder for Total Operating Expenses
            0, # Placeholder for Net Operating Income
            210000, 52000, 158000,
            0, # Placeholder for Net Income (Loss)
            None,
            None,
            200, 15300, 7.6, 0, # Placeholder for Occupancy Rate
            5100
        ],
        '2024-Q2': [
            10500000, 520000, 11020000,
            4100000, 1600000, 720000,
            310000, 1100000, 7830000,
            3190000,
            220000, 55000, 165000,
            3355000,
            None,
            None,
            205, 15800, 7.7, 0, # Placeholder for Occupancy Rate
            5250
        ]
    }

    df = pd.DataFrame(data)

    # Calculate dependent values
    q4_days = 92
    q1_days = 90
    q2_days = 91

    # --- Calculations for 2023-Q4 ---
    df.loc[df['Financial Metric'] == 'Occupancy Rate (%)', '2023-Q4'] = round(
        (df.loc[df['Financial Metric'] == 'Patient Days', '2023-Q4'].values[0] /
        (df.loc[df['Financial Metric'] == 'Number of Beds', '2023-Q4'].values[0] * q4_days)) * 100, 2
    )

    # --- Calculations for 2024-Q1 ---
    q1_salaries = df.loc[df['Financial Metric'] == 'Salaries and Wages', '2024-Q1'].values[0]
    q1_med_supplies = df.loc[df['Financial Metric'] == 'Medical Supplies', '2024-Q1'].values[0]
    q1_dep_amort = df.loc[df['Financial Metric'] == 'Depreciation and Amortization', '2024-Q1'].values[0]
    q1_interest = df.loc[df['Financial Metric'] == 'Interest Expense', '2024-Q1'].values[0]
    q1_other_op_exp = df.loc[df['Financial Metric'] == 'Other Operating Expenses', '2024-Q1'].values[0]

    q1_total_op_exp = q1_salaries + q1_med_supplies + q1_dep_amort + q1_interest + q1_other_op_exp
    df.loc[df['Financial Metric'] == 'Total Operating Expenses', '2024-Q1'] = q1_total_op_exp

    q1_total_op_rev = df.loc[df['Financial Metric'] == 'Total Operating Revenue', '2024-Q1'].values[0]
    q1_net_op_income = q1_total_op_rev - q1_total_op_exp
    df.loc[df['Financial Metric'] == 'Net Operating Income', '2024-Q1'] = q1_net_op_income

    q1_net_non_op_income = df.loc[df['Financial Metric'] == 'Net Non-Operating Income/Loss', '2024-Q1'].values[0]
    df.loc[df['Financial Metric'] == 'Net Income (Loss)', '2024-Q1'] = q1_net_op_income + q1_net_non_op_income

    df.loc[df['Financial Metric'] == 'Occupancy Rate (%)', '2024-Q1'] = round(
        (df.loc[df['Financial Metric'] == 'Patient Days', '2024-Q1'].values[0] /
        (df.loc[df['Financial Metric'] == 'Number of Beds', '2024-Q1'].values[0] * q1_days)) * 100, 2
    )

    # --- Calculations for 2024-Q2 ---
    df.loc[df['Financial Metric'] == 'Occupancy Rate (%)', '2024-Q2'] = round(
        (df.loc[df['Financial Metric'] == 'Patient Days', '2024-Q2'].values[0] /
        (df.loc[df['Financial Metric'] == 'Number of Beds', '2024-Q2'].values[0] * q2_days)) * 100, 2
    )

    sheet_name = "Financials_And_Stats"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

        worksheet = writer.sheets[sheet_name]
        for column_cells in worksheet.columns:
            length = 0
            for cell in column_cells:
                if cell.value is not None:
                    length = max(length, len(str(cell.value)))
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2

if __name__ == "__main__":
    # This script is intended to be in 'financial_report_analyzer' directory.
    # The output file will also be in 'financial_report_analyzer'.
    output_filename = "sample_healthcare_financials.xlsx"

    # This script is intended to be in 'financial_report_analyzer' directory.
    # The output file will also be in 'financial_report_analyzer'.

    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, "sample_healthcare_financials.xlsx")

    # Ensure the directory for the output file exists (it should be script_dir)
    os.makedirs(script_dir, exist_ok=True)

    create_sample_excel(output_filename)
    print(f"Sample Excel file created: '{output_filename}'")
