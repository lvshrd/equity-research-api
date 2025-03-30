from langchain_anthropic import ChatAnthropic
from app.agents.tools.company_data_tool import CompanyDataTool
from app.agents.tools.yahoo_finance_tool import YahooFinanceTool
from langchain.agents import AgentExecutor
from langgraph.prebuilt import create_react_agent

class AnthropicAgent:

        def __init__(self, tools: list, model: object):  # Add constructor
            self.tools = tools
            self.model = model

        def _base_prompt(self) -> str:
            return """You are a professional equity research analyst tasked with generating comprehensive research reports.
            Follow these steps to generate a high-quality equity research report:
            1. Analyze company fundamentals.
            2. Analyze the financial data using the financial_analysis tool
            3. Synthesize all information into a comprehensive research report
            Your report should include:
            - Executive Summary
            - Company Overview
            - Financial Analysis (including key metrics and ratios)
            - Historical Performance
            - Market Position and Competitive Analysis
            - Investment Thesis
            - Risks and Challenges
            - Outlook and Recommendations
            Always think step by step and use the appropriate tools to gather the information needed. 
            Use professional tone and include relevant data points. Format using markdown.
            """
        
        def build_executor(self) -> AgentExecutor: 
            """Build agent executor with proper prompt integration"""
            agent_executor = create_react_agent(
                model=self.model,
                tools= self.tools,
                prompt=self._base_prompt(),
                )

            return agent_executor
        
        @classmethod
        def initialize(cls, model:str,api_key:str):

            llm = ChatAnthropic(
                model = model,
                temperature=0.2,
                verbose= True,
                api_key = api_key 
            )
            tools = [CompanyDataTool(),
                    YahooFinanceTool()]

            return cls(tools=tools, model=llm)