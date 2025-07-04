import re

def generate_llm_prompt(trend_analyzer_summary: str, company_name: str = "the organization") -> str:
    """
    Formats the trend analysis summary into a prompt for an LLM.
    """
    prompt = f"Please provide a concise, narrative summary of the financial performance of {company_name} "
    prompt += "based on the following key observations. Focus on the most important trends and insights "
    prompt += "that would be relevant for a business stakeholder. Combine related points where possible.\n\n"
    prompt += "Key Observations:\n"
    prompt += trend_analyzer_summary
    prompt += "\n\nNarrative Summary:"
    return prompt

def get_simulated_llm_summary(prompt: str) -> str:
    """
    Simulates an LLM generating a narrative summary from a prompt.
    This is a rule-based mock and does not call any external LLM.
    """
    narrative = f"--- Simulated LLM Narrative Summary (Illustrative) ---\n\n"
    narrative += f"Overall, the financial report for the organization indicates several noteworthy trends. "

    # Extract key pieces of information using regex from the prompt's "Key Observations"
    # This is a very simplified approach. A real LLM would understand context much better.

    observations = prompt.split("Key Observations:\n")[1].split("\n\nNarrative Summary:")[0]

    # Try to find overall revenue trends
    revenue_growth_streaks = []
    revenue_decline_streaks = []


    # Simplified parsing for mock LLM
    # Look for any mention of revenue growth/decline
    if "Total Patient Revenue" in observations or "Total Operating Revenue" in observations:
        if "Consecutive Growth" in observations and "Revenue" in observations.split("Consecutive Growth")[1].split("\n")[0]: # Check if "Revenue" is part of the growth line
            narrative += "Revenue has shown a positive trend. "
        elif "Consecutive Decline" in observations and "Revenue" in observations.split("Consecutive Decline")[1].split("\n")[0]:
             narrative += "There are indications of a decline in revenue. "

    # Look for any mention of profit growth/decline or significant deviation
    if "Net Operating Income" in observations or "Net Income (Loss)" in observations:
        profit_section = ""
        if "Analysis for Metric: Net Operating Income" in observations:
            profit_section = observations.split("Analysis for Metric: Net Operating Income")[1]
            if "Analysis for Metric:" in profit_section:
                 profit_section = profit_section.split("Analysis for Metric:")[0]
        elif "Analysis for Metric: Net Income (Loss)" in observations:
            profit_section = observations.split("Analysis for Metric: Net Income (Loss)")[1]
            if "Analysis for Metric:" in profit_section:
                 profit_section = profit_section.split("Analysis for Metric:")[0]

        if "Consecutive Growth" in profit_section:
            narrative += "Profitability appears to be improving. "
        elif "Consecutive Decline" in profit_section:
            narrative += "Profitability shows some concerning declining trends. "
        elif "significantly above average" in profit_section:
            narrative += "Profitability was notably above average in some periods. "
        elif "significantly below average" in profit_section:
            narrative += "Profitability was notably below average in some periods. "

    # Mention operational metrics if specific keywords found
    op_keywords = ["Patient Days", "Occupancy Rate", "Emergency Room Visits"]
    op_mentions = []
    for keyword in op_keywords:
        if keyword in observations:
            # Check if there's a meaningful analysis line for this keyword
            if f"Analysis for Metric: {keyword}" in observations or \
               (keyword in observations and ("Consecutive Growth" in observations or "Consecutive Decline" in observations or "Deviation" in observations)):
                op_mentions.append(keyword)

    if op_mentions:
        narrative += f"Key operational metrics such as {', '.join(op_mentions)} also showed some activity. "

    # Fallback message if no specific points were strongly extracted by the simplified rules
    initial_narrative_base = "--- Simulated LLM Narrative Summary (Illustrative) ---\n\nOverall, the financial report for the organization indicates several noteworthy trends. "
    if narrative.strip() == initial_narrative_base.strip(): # Check if only the base sentence is there
        if "Analysis for Metric:" in observations: # Check if there was any analysis at all
             narrative += "The detailed analysis shows various trends across different metrics. "
        else:
            narrative += "No specific strong trends were automatically highlighted by this simplified simulation. Please review the detailed observations provided in the prompt."
    else:
        narrative += "\n\nIt is advisable to look deeper into these areas to understand the underlying drivers. "
    narrative += "(Note: This is a simulated summary based on structured data.)"

    return narrative

if __name__ == "__main__":
    # Example usage with a dummy trend_analyzer_summary
    sample_trend_summary = """Trend Analysis Summary:

Metric Averages:
  - Total Patient Revenue: 10,233,333.33
  - Net Income (Loss): 3,236,000.00

Analysis for Metric: Total Patient Revenue
  - Consecutive Growth: 2 periods, from 2023-Q4 (10,000,000.00) to 2024-Q2 (10,500,000.00). Change first noted in 2024-Q1.
  - Deviation: In 2024-Q2, value 10,500,000.00 was 2.61% above average (10,233,333.33), which is not significant.

Analysis for Metric: Net Income (Loss)
  - Consecutive Growth: 2 periods, from 2023-Q4 (3,150,000.00) to 2024-Q2 (3,355,000.00). Change first noted in 2024-Q1.
  - Deviation: In 2024-Q2, value 3,355,000.00 was 3.68% above average (3,236,000.00), which is not significant.
"""

    prompt_text = generate_llm_prompt(sample_trend_summary, company_name="HealthCorp Inc.")
    print("--- Generated LLM Prompt ---")
    print(prompt_text)

    simulated_summary = get_simulated_llm_summary(prompt_text)
    print("\n--- Simulated LLM Summary ---")
    print(simulated_summary)

    empty_summary = ""
    prompt_empty = generate_llm_prompt(empty_summary)
    print("\n--- Prompt with empty summary ---")
    print(prompt_empty)
    sim_empty = get_simulated_llm_summary(prompt_empty)
    print("\n--- Simulated LLM for empty summary ---")
    print(sim_empty)

    summary_with_decline = """Trend Analysis Summary:
Metric Averages:
  - Total Patient Revenue: 9,000,000.00
Analysis for Metric: Total Patient Revenue
  - Consecutive Decline: 2 periods, from 2023-Q4 (10,000,000.00) to 2024-Q2 (8,000,000.00). Change first noted in 2024-Q1.
    """
    prompt_decline = generate_llm_prompt(summary_with_decline)
    print("\n--- Prompt with decline summary ---")
    print(prompt_decline)
    sim_decline = get_simulated_llm_summary(prompt_decline)
    print("\n--- Simulated LLM for decline summary ---")
    print(sim_decline)


    summary_profit_deviation = """Trend Analysis Summary:
Metric Averages:
  - Net Operating Income: 500,000.00
Analysis for Metric: Net Operating Income
  - Deviation: In 2024-Q1, value 750,000.00 was 50.0% above average (500,000.00), which is significantly above average.
    """
    prompt_profit_dev = generate_llm_prompt(summary_profit_deviation)
    print("\n--- Prompt with profit deviation ---")
    print(prompt_profit_dev)
    sim_profit_dev = get_simulated_llm_summary(prompt_profit_dev)
    print("\n--- Simulated LLM for profit deviation ---")
    print(sim_profit_dev)
