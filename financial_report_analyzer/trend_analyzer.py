import pandas as pd
import numpy as np

class TrendAnalyzer:
    def __init__(self, metrics_df, period_over_period_change_df):
        """
        Initializes the TrendAnalyzer with metrics data and PoP change data.

        Args:
            metrics_df (pd.DataFrame): DataFrame with metrics as index (rows) and periods as columns.
            period_over_period_change_df (pd.DataFrame): DataFrame with PoP % changes, metrics as index.
        """
        if not isinstance(metrics_df, pd.DataFrame) or metrics_df.empty:
            raise ValueError("Metrics DataFrame cannot be empty.")
        if not isinstance(period_over_period_change_df, pd.DataFrame) or period_over_period_change_df.empty:
            raise ValueError("Period-over-period change DataFrame cannot be empty.")

        # Ensure metrics are rows and periods are columns
        if not metrics_df.index.name == period_over_period_change_df.index.name: # A basic check
             # This might need more robust validation depending on actual index names
            print("Warning: Metrics DataFrame and PoP Change DataFrame might have different index structures.")

        self.metrics_df = metrics_df.apply(pd.to_numeric, errors='coerce')
        self.pop_change_df = period_over_period_change_df.apply(pd.to_numeric, errors='coerce')

    def get_consecutive_streaks(self, metric_name, min_streak_length=2, trend_type='growth'):
        """
        Identifies consecutive periods of growth or decline for a specific metric.

        Args:
            metric_name (str): The name of the metric to analyze.
            min_streak_length (int): Minimum number of consecutive periods to count as a streak.
            trend_type (str): 'growth' for positive PoP change, 'decline' for negative.

        Returns:
            list: A list of dictionaries, each describing a streak found.
        """
        if metric_name not in self.pop_change_df.index:
            # Check if metric is in the original metrics_df, if so, it implies no PoP data (e.g. single period)
            if metric_name in self.metrics_df.index:
                return [] # No PoP data to analyze for streaks
            return [{"error": f"Metric '{metric_name}' not found in PoP change data."}]

        streaks = []
        # Ensure we are working with a series that has a named index (periods)
        metric_pop_series = self.pop_change_df.loc[metric_name].dropna()

        if metric_pop_series.empty or len(metric_pop_series) < 1: # Not enough data for a streak involving change
            return []

        current_streak = 0
        streak_start_period_label = None # Label of the period where the streak of changes begins

        for i in range(len(metric_pop_series)):
            change = metric_pop_series.iloc[i]
            current_period_label = metric_pop_series.index[i]

            is_trend_match = (trend_type == 'growth' and change > 0) or \
                             (trend_type == 'decline' and change < 0)

            if is_trend_match:
                if current_streak == 0:
                    streak_start_period_label = current_period_label
                current_streak += 1
            else:
                if current_streak >= min_streak_length:
                    # Streak ended one period before current 'i'
                    end_of_change_period_label = metric_pop_series.index[i-1]

                    # Determine the original data points involved in the streak
                    # The PoP change for period P is based on values at P and P-1.
                    # A streak of 'current_streak' changes involves 'current_streak + 1' original data points.
                    original_metric_series = self.metrics_df.loc[metric_name]

                    # The first period of change is streak_start_period_label.
                    # The original data point *before* this first change is needed.
                    idx_of_first_change_period_in_orig = original_metric_series.index.get_loc(streak_start_period_label)

                    streak_values_start_idx = idx_of_first_change_period_in_orig - 1
                    streak_values_end_idx = idx_of_first_change_period_in_orig -1 + current_streak

                    streak_period_labels_in_orig = original_metric_series.index[streak_values_start_idx : streak_values_end_idx + 1]
                    streak_values = original_metric_series[streak_period_labels_in_orig].tolist()

                    streaks.append({
                        'metric': metric_name,
                        'streak_type': trend_type,
                        'length': current_streak, # Number of consecutive changes
                        'first_period_of_change': streak_start_period_label,
                        'last_period_of_change': end_of_change_period_label,
                        'streak_data_from_period': streak_period_labels_in_orig[0],
                        'streak_data_to_period': streak_period_labels_in_orig[-1],
                        'values_over_streak': streak_values
                    })
                current_streak = 0
                streak_start_period_label = None

        # Check for a streak at the end of the series
        if current_streak >= min_streak_length:
            end_of_change_period_label = metric_pop_series.index[len(metric_pop_series)-1]
            original_metric_series = self.metrics_df.loc[metric_name]
            idx_of_first_change_period_in_orig = original_metric_series.index.get_loc(streak_start_period_label)

            streak_values_start_idx = idx_of_first_change_period_in_orig - 1
            streak_values_end_idx = idx_of_first_change_period_in_orig - 1 + current_streak

            streak_period_labels_in_orig = original_metric_series.index[streak_values_start_idx : streak_values_end_idx + 1]
            streak_values = original_metric_series[streak_period_labels_in_orig].tolist()

            streaks.append({
                'metric': metric_name,
                'streak_type': trend_type,
                'length': current_streak,
                'first_period_of_change': streak_start_period_label,
                'last_period_of_change': end_of_change_period_label,
                'streak_data_from_period': streak_period_labels_in_orig[0],
                'streak_data_to_period': streak_period_labels_in_orig[-1],
                'values_over_streak': streak_values
            })
        return streaks

    def get_metric_averages(self):
        """Calculates the average for each metric across all periods."""
        return self.metrics_df.mean(axis=1).rename('Average') # axis=1 for row-wise mean

    def compare_to_average(self, metric_name, deviation_threshold_pct=10):
        """
        Identifies periods where a metric is significantly above or below its average.

        Args:
            metric_name (str): The name of the metric to analyze.
            deviation_threshold_pct (float): Percentage threshold for significant deviation.

        Returns:
            list: Dictionaries describing significant deviations.
                  e.g., [{'metric': metric_name, 'period': '2023-Q2', 'value': X,
                          'average': Y, 'deviation_pct': Z, 'status': 'significantly above average'}]
        """
        if metric_name not in self.metrics_df.index:
            return [{"error": f"Metric '{metric_name}' not found."}]

        metric_series = self.metrics_df.loc[metric_name].dropna()
        if metric_series.empty:
            return []

        metric_avg = metric_series.mean()
        results = []

        for period, value in metric_series.items():
            if pd.isna(value) or pd.isna(metric_avg) or metric_avg == 0: # Avoid division by zero or NaN issues
                deviation_pct = 0
            else:
                deviation_pct = ((value - metric_avg) / metric_avg) * 100

            status = None
            if deviation_pct > deviation_threshold_pct:
                status = f"significantly above average (>{deviation_threshold_pct}%)"
            elif deviation_pct < -deviation_threshold_pct:
                status = f"significantly below average (<{-deviation_threshold_pct}%)"

            if status:
                results.append({
                    'metric': metric_name,
                    'period': period,
                    'value': value,
                    'average': round(metric_avg, 2),
                    'deviation_pct': round(deviation_pct, 2),
                    'status': status
                })
        return results

    def generate_text_summary(self, metrics_to_analyze=None, streak_min_length=2, avg_dev_threshold_pct=10):
        """
        Generates a textual summary of advanced trend analysis.
        """
        if metrics_to_analyze is None:
            metrics_to_analyze = self.metrics_df.index.tolist()

        summary_lines = ["Trend Analysis Summary:\n"]

        averages = self.get_metric_averages()
        summary_lines.append("Metric Averages:")
        for metric, avg_val in averages.items():
            if metric in metrics_to_analyze :
                 summary_lines.append(f"  - {metric}: {avg_val:,.2f}")
        summary_lines.append("\n")

        for metric in metrics_to_analyze:
            if metric not in self.metrics_df.index:
                summary_lines.append(f"Metric '{metric}' not found for detailed analysis.\n")
                continue

            summary_lines.append(f"Analysis for Metric: {metric}")

            # Growth Streaks
            growth_streaks = self.get_consecutive_streaks(metric, min_streak_length=streak_min_length, trend_type='growth')
            if growth_streaks and not ("error" in growth_streaks[0]):
                for streak in growth_streaks:
                    summary_lines.append(
                        f"  - Consecutive Growth: {streak['length']} periods, "
                        f"from {streak['streak_data_from_period']} ({streak['values_over_streak'][0]:,.2f}) "
                        f"to {streak['streak_data_to_period']} ({streak['values_over_streak'][-1]:,.2f}). "
                        f"Change first noted in {streak['first_period_of_change']}."
                    )

            # Decline Streaks
            decline_streaks = self.get_consecutive_streaks(metric, min_streak_length=streak_min_length, trend_type='decline')
            if decline_streaks and not ("error" in decline_streaks[0]):
                 for streak in decline_streaks:
                    summary_lines.append(
                        f"  - Consecutive Decline: {streak['length']} periods, "
                        f"from {streak['streak_data_from_period']} ({streak['values_over_streak'][0]:,.2f}) "
                        f"to {streak['streak_data_to_period']} ({streak['values_over_streak'][-1]:,.2f}). "
                        f"Change first noted in {streak['first_period_of_change']}."
                    )

            # Deviation from Average
            deviations = self.compare_to_average(metric, deviation_threshold_pct=avg_dev_threshold_pct)
            if deviations and not ("error" in deviations[0]):
                for dev in deviations:
                    summary_lines.append(
                        f"  - Deviation: In {dev['period']}, value {dev['value']:,.2f} was "
                        f"{dev['deviation_pct']}% {'above' if dev['deviation_pct'] > 0 else 'below'} average ({dev['average']:,.2f}), "
                        f"which is {dev['status'].split(' (')[0]}."
                    ) # Simplified status output
            summary_lines.append("\n")

        return "\n".join(summary_lines)

# This main block is for testing TrendAnalyzer independently.
# Integration will happen in report_parser.py's main or a new main script.
if __name__ == "__main__":
    # Sample data (mimicking what ExcelReportParser would provide)
    metrics_data = {
        'Revenue': {'2023-Q1': 100, '2023-Q2': 110, '2023-Q3': 120, '2023-Q4': 115, '2024-Q1': 130},
        'Expenses': {'2023-Q1': 80, '2023-Q2': 85, '2023-Q3': 82, '2023-Q4': 90, '2024-Q1': 88},
        'Profit': {'2023-Q1': 20, '2023-Q2': 25, '2023-Q3': 38, '2023-Q4': 25, '2024-Q1': 42},
        'Users': {'2023-Q1': 1000, '2023-Q2': 950, '2023-Q3': 900, '2023-Q4': 850, '2024-Q1': 800} # Decline streak
    }
    # metrics_df_test should have metrics as index, periods as columns.
    metrics_df_test = pd.DataFrame(metrics_data).T
    metrics_df_test.index.name = "Metric" # Set index name for clarity

    # Calculate PoP change for the test data (original PoP calc was fine as it used .T)
    # Ensure pop_change_df_test also has metrics as index
    pop_change_df_test = metrics_df_test.T.pct_change().T * 100

    analyzer = TrendAnalyzer(metrics_df_test, pop_change_df_test)

    print("--- Testing Consecutive Streaks ---")
    revenue_growth_streaks = analyzer.get_consecutive_streaks('Revenue', min_streak_length=2, trend_type='growth')
    print(f"Revenue Growth Streaks (min 2): {revenue_growth_streaks}")

    user_decline_streaks = analyzer.get_consecutive_streaks('Users', min_streak_length=3, trend_type='decline')
    print(f"User Decline Streaks (min 3): {user_decline_streaks}")

    print("\n--- Testing Metric Averages ---")
    averages_test = analyzer.get_metric_averages() # Should now be correct
    print(averages_test)

    print("\n--- Testing Comparison to Average ---")
    profit_deviations = analyzer.compare_to_average('Profit', deviation_threshold_pct=15)
    print(f"Profit Deviations from Avg (threshold 15%): {profit_deviations}")

    print("\n--- Testing Text Summary ---")
    # Ensure the metrics_to_analyze list matches the index of metrics_df_test
    summary = analyzer.generate_text_summary(metrics_to_analyze=['Revenue', 'Users', 'Profit'], streak_min_length=2, avg_dev_threshold_pct=15)
    print(summary)

    summary_all = analyzer.generate_text_summary() # All metrics, default thresholds
    print("\n--- Full Summary (All Metrics, Default Thresholds) ---")
    print(summary_all)

    # Test with data having only two periods (edge case for streaks)
    metrics_data_short = {
        'Revenue': {'2024-Q1': 100, '2024-Q2': 110}, # 1 growth
        'Expenses': {'2024-Q1': 80, '2024-Q2': 70}   # 1 decline
    }
    metrics_df_short = pd.DataFrame(metrics_data_short).T
    metrics_df_short.index.name = "Metric"
    pop_change_df_short = metrics_df_short.T.pct_change().T * 100
    analyzer_short = TrendAnalyzer(metrics_df_short, pop_change_df_short)
    print("\n--- Short Data Test (Revenue Growth Streaks, min_streak_length=1) ---")
    revenue_growth_short = analyzer_short.get_consecutive_streaks('Revenue', min_streak_length=1, trend_type='growth')
    print(revenue_growth_short)
    print("\n--- Short Data Summary ---")
    summary_short = analyzer_short.generate_text_summary()
    print(summary_short)

    # Test with NaN values in metrics_df
    metrics_data_nan = {
        'Revenue': {'2023-Q1': 100, '2023-Q2': np.nan, '2023-Q3': 120},
    }
    metrics_df_nan = pd.DataFrame(metrics_data_nan).T
    metrics_df_nan.index.name = "Metric"
    pop_change_df_nan = metrics_df_nan.T.pct_change().T * 100
    analyzer_nan = TrendAnalyzer(metrics_df_nan, pop_change_df_nan)
    print("\n--- NaN Data Test (Revenue Growth Streaks, min_streak_length=1) ---")
    revenue_growth_nan = analyzer_nan.get_consecutive_streaks('Revenue', min_streak_length=1, trend_type='growth')
    print(revenue_growth_nan) # Should be empty or handle gracefully
    print("\n--- NaN Data Summary ---")
    summary_nan = analyzer_nan.generate_text_summary()
    print(summary_nan)

    # Test with a metric that has no PoP data (e.g. all NaNs or single period)
    metrics_data_single_period = {
        'Revenue': {'2023-Q1': 100},
        'Expenses': {'2023-Q1': np.nan, '2023-Q2': np.nan}
    }
    metrics_df_single = pd.DataFrame(metrics_data_single_period).T
    metrics_df_single.index.name = "Metric"
    pop_change_df_single = metrics_df_single.T.pct_change().T * 100
    analyzer_single = TrendAnalyzer(metrics_df_single, pop_change_df_single)
    print("\n--- Single Period/All NaN PoP Data Test ---")
    revenue_streaks_single = analyzer_single.get_consecutive_streaks('Revenue', min_streak_length=1)
    print(f"Revenue streaks (single period): {revenue_streaks_single}")
    expenses_streaks_single = analyzer_single.get_consecutive_streaks('Expenses', min_streak_length=1)
    print(f"Expenses streaks (all NaN PoP): {expenses_streaks_single}")
    summary_single = analyzer_single.generate_text_summary()
    print(summary_single)

    # Test with a metric that has no change (flat)
    metrics_data_flat = {
        'Revenue': {'2023-Q1': 100, '2023-Q2': 100, '2023-Q3': 100},
    }
    metrics_df_flat = pd.DataFrame(metrics_data_flat).T
    metrics_df_flat.index.name = "Metric"
    pop_change_df_flat = metrics_df_flat.T.pct_change().T * 100 # will be all 0s
    analyzer_flat = TrendAnalyzer(metrics_df_flat, pop_change_df_flat)
    print("\n--- Flat Data Test ---")
    revenue_streaks_flat_growth = analyzer_flat.get_consecutive_streaks('Revenue', min_streak_length=1, trend_type='growth')
    print(f"Revenue growth streaks (flat data): {revenue_streaks_flat_growth}") # Should be empty
    revenue_streaks_flat_decline = analyzer_flat.get_consecutive_streaks('Revenue', min_streak_length=1, trend_type='decline')
    print(f"Revenue decline streaks (flat data): {revenue_streaks_flat_decline}") # Should be empty
    summary_flat = analyzer_flat.generate_text_summary()
    print(summary_flat)

fi_data = {
    'Total Patient Revenue': {'2023-Q4': 10000000.00, '2024-Q1': 10200000.0, '2024-Q2': 10500000.0},
    'Total Operating Revenue': {'2023-Q4': 10500000.00, '2024-Q1': 10710000.0, '2024-Q2': 11020000.0},
    'Total Operating Expenses': {'2023-Q4': 7500000.00, '2024-Q1': 7665000.0, '2024-Q2': 7830000.0},
    'Net Operating Income': {'2023-Q4': 3000000.00, '2024-Q1': 3045000.0, '2024-Q2': 3190000.0},
    'Net Income (Loss)': {'2023-Q4': 3150000.00, '2024-Q1': 3203000.0, '2024-Q2': 3355000.0},
    'Number of Beds': {'2023-Q4': 200.00, '2024-Q1': 200.0, '2024-Q2': 205.0}, # Mixed
    'Patient Days': {'2023-Q4': 15000.00, '2024-Q1': 15300.0, '2024-Q2': 15800.0},
    'Average Length of Stay (Days)': {'2023-Q4': 7.50, '2024-Q1': 7.6, '2024-Q2': 7.7},
    'Occupancy Rate (%)': {'2023-Q4': 81.52, '2024-Q1': 85.0, '2024-Q2': 84.7}, # Mixed
    'Emergency Room Visits': {'2023-Q4': 5000.00, '2024-Q1': 5100.0, '2024-Q2': 5250.0}
}
fi_metrics_df = pd.DataFrame(fi_data).T # Transpose here
fi_metrics_df.index.name = "Metric"
fi_pop_change_df = fi_metrics_df.T.pct_change().T * 100
analyzer_fi = TrendAnalyzer(fi_metrics_df, fi_pop_change_df)
print("\n--- Financial Report Sample Data Summary ---")
fi_summary = analyzer_fi.generate_text_summary(streak_min_length=1) # min_streak_length=1 to catch 2-period changes
print(fi_summary)
