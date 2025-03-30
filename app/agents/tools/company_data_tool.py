# app/agents/tools/company_data_tool.py
from typing import Optional, Dict, Any
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field
from app.data_loader import DataLoader as DLoader

class CompanyDataInput(BaseModel):
    company_id: str = Field(description="Company ID to fetch data for")

# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class CompanyDataTool(BaseTool):
    name: str = "company_data_loader"
    description: str = "tool for fetching company data from local database according to company_id"
    args_schema: Optional[ArgsSchema] = CompanyDataInput
    return_direct: bool = False

    def _run(
        self, company_id: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Use the tool."""
        dloader= DLoader()
        return dloader.get_company_data(company_id)

    # async def _arun(
    #     self,
    #     company_id: str,
    #     run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    # ) -> Dict[str, Any]:
    #     """Use the tool asynchronously."""
    #     # If the calculation is cheap, you can just delegate to the sync implementation
    #     # as shown below.
    #     # If the sync calculation is expensive, you should delete the entire _arun method.
    #     # LangChain will automatically provide a better implementation that will
    #     # kick off the task in a thread to make sure it doesn't block other async code.
    #     return self._run(company_id, run_manager=run_manager.get_sync())