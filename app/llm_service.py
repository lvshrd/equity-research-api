# app/llm_service.py
import os
import httpx
from typing import Optional
import toml

class AnthropicService:
    def __init__(self):
        self.api_key = toml.load("config.toml")["AGENT"]["ANTHROPIC_API_KEY"]
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
        return f"""
        Generate a comprehensive equity research report for {company_data['metadata']['company_name']} 
        ({company_data['metadata']['ticker']}). Include the following sections:

        1. Company Overview
        2. Financial Highlights
        3. Risk Analysis
        4. Investment Recommendation

        Use professional tone and include relevant data points. Format using markdown.
        """