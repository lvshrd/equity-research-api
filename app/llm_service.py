# app/llm_service.py
import os
import httpx
from typing import Optional
from config import CONFIG

class AnthropicService:
    def __init__(self):
        self.api_key = CONFIG["anthropic"]["api_key"]
        self.base_url = "https://api.anthropic.com/v1"
        self.headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

    async def generate_report(self, prompt: str, model: str = "claude-instant-1") -> Optional[str]:
        """Generate report using Anthropic API"""
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    f"{self.base_url}/complete",
                    json={
                        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
                        "model": model,
                        "max_tokens_to_sample": 4000,
                    },
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()["completion"]
                
        except (httpx.HTTPError, KeyError) as e:
            print(f"LLM API Error: {str(e)}")
            return None

    def build_prompt(self, company_data: dict) -> str:
        """Construct research report prompt"""
        recent_financials = []
        if company_data.get("financial_data"):
            # 按年份排序，取最近的3年
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