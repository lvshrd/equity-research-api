# app/llm_service.py
from typing import Optional
from config import CONFIG
import anthropic

class AnthropicService:
    def __init__(self):
        self.api_key = CONFIG["anthropic"]["api_key"]

    async def generate_report(self, prompt: str, model: str = "claude-3-haiku-20240307") -> Optional[str]:
        """Generate report using Anthropic API"""
        try:
            client = anthropic.AsyncAnthropic(
                api_key=self.api_key
            )
            response = await client.messages.create(
                model=model,
                max_tokens=4000,
                messages=[{
                    "role": "user", "content": prompt}
                    ]
            )
            return response.content[0].text
                
        except Exception as e:
            raise RuntimeError(f"LLM API request failed: {str(e)}")

    def build_prompt(self, company_data: dict) -> str:
        """Construct research report prompt"""
        recent_financials = []
        if company_data.get("financial_data"):
            # Sort according to year, latest 3 years here
            sorted_data = sorted(
                company_data["financial_data"], 
                key=lambda x: x.get("fiscal_year", 0), 
                reverse=True
            )[:3]
            recent_financials = sorted_data
        
        financial_text = ""
        if recent_financials:
            financial_text = "Recent financial data:\n"
            for item in recent_financials:
                year = item.get("fiscal_year", "N/A")
                revenue = item.get("total_revenue", "N/A")
                net_income = item.get("net_income", "N/A")
                financial_text += f"- Year {year}: Revenue: {revenue}, Net Income: {net_income}\n"
        return f"""
        Generate a comprehensive equity research report for {company_data['metadata']['company_name']} 
        ({company_data['metadata']['ticker']}). 
        
        Company Information:
        - Industry Sector: {company_data['metadata'].get('industry_sector_num', 'N/A')}
        - Country: {company_data['metadata'].get('country_name', 'N/A')}
        
        {financial_text}
        
        Include the following sections:

        1. Executive Summary
        2. Company Overview
        3. Industry Analysis
        4. Financial Highlights
        5. Valuation
        6. Investment Recommendation
        7. Risks and Challenges
        
        Use professional tone and include relevant data points. Format using markdown.
        """