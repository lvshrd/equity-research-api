# app/llm.py
import anthropic
import toml
import json

def get_anthropic_client():
    config = toml.load("config.toml")
    api_key = config["AGENT"]["ANTHROPIC_API_KEY"]
    return anthropic.Anthropic(api_key=api_key)

def generate_equity_research_report(company_id: str):
    client = get_anthropic_client()
    
    # This is a simplified prompt - in a real application, you would
    # gather company data from financial APIs and include it in the prompt
    prompt = f"""
    Generate a comprehensive equity research report for company with ID {company_id}.
    
    The report should include:
    1. Executive Summary
    2. Company Overview
    3. Industry Analysis
    4. Financial Analysis
    5. Valuation
    6. Investment Recommendation
    7. Risks and Challenges
    
    Format the report in a professional manner suitable for investors.
    """
    
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.content[0].text