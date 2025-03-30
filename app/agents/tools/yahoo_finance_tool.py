# app/agents/tools/yahoo_finance_tool.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from langchain_core.tools.base import ArgsSchema
from pydantic import BaseModel, Field
import asyncio

class YahooFinanceInput(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    period: str = Field("1y", description="Time period for historical data")

class YahooFinanceTool(BaseTool):
    """Tool for fetching stock data from Yahoo Finance"""
    name: str = "yahoo_finance"
    description: str = "tool Fetches stock data from Yahoo Finance API"
    args_schema: Optional[ArgsSchema] = YahooFinanceInput
    return_direct: bool = False

    def _run(self, ticker: str, period: str = "1m") -> Dict[str, Any]:
        try:
            result = asyncio.run(self.fetch_stock_data(ticker, period))
            if "error" in result:
                return f"Error occurred while fetching stock data: {result['error']}"
            return result
        except AttributeError as e:
            if "'NoneType' object has no attribute 'update'" in str(e):
                return "Can not get that stock's data, please check the stock code and try again later."
            else:
                return f"Something unexpected happened: {e}"
        except Exception as e:
            return f"Unknown error occurred: {e}"

    async def _arun(self, ticker: str, period: str = "1m") -> Dict[str, Any]:
        """Asynchronous execution method"""
        try:
            result = await self.fetch_stock_data(ticker, period)
            if "error" in result:
                return f"Error occurred while fetching stock data: {result['error']}"
            return result
        except AttributeError as e:
            if "'NoneType' object has no attribute 'update'" in str(e):
                return "Can not get that stock's data, please check the stock code and try again later."
            else:
                return f"Something unexpected happened: {e}"
        except Exception as e:
            return f"Unknown error occurred: {e}"


    async def fetch_stock_data(self, ticker: str, period: str = "1m") -> Dict[str, Any]:
        """
        Fetch essential stock data from Yahoo Finance.

        Args:
            ticker: Stock ticker symbol
            period: Time period for historical data (e.g., "1mo", "6mo", "1y", "5y")

        Returns:
            Dictionary containing key stock data.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            simplified_info = {
                'symbol': info.get('symbol'),
                'shortName': info.get('shortName'),
                'industry': info.get('industry'),
                'sector': info.get('sector'),
                'currentPrice': info.get('currentPrice'),
                'previousClose': info.get('previousClose'),
                'marketCap': info.get('marketCap'),
                'trailingPE': info.get('trailingPE'),
                'forwardPE': info.get('forwardPE'),
                'recommendationMean': info.get('recommendationMean')
            }

            # Fetch historical data
            end_date = datetime.now()
            if period.endswith('y'):
                start_date = end_date - timedelta(days=365 * int(period[:-1]))
                max_history_points = 90
            elif period.endswith('m'):
                start_date = end_date - timedelta(days=30 * int(period[:-1]))
                max_history_points = 60
            else:
                start_date = end_date - timedelta(days=30)  # Default to 1 months
                max_history_points = 30

            hist = stock.history(start=start_date, end=end_date)[['Close', 'Volume']] # Only get Close and Volume
            if not hist.empty:
                hist_trimmed = hist.tail(max_history_points).reset_index().to_dict(orient="records")
            else:
                hist_trimmed = []


            # Fetch key financial statements (simplify to annual)
            financials = stock.financials.to_dict() if hasattr(stock, 'financials') else {}
            latest_financials = financials.get(list(financials.keys())[0] if financials else {}, {})
            simplified_financials = {
                'totalRevenue': latest_financials.get('Total Revenue'),
                'netIncome': latest_financials.get('Net Income'),
                'grossProfit': latest_financials.get('Gross Profit')
            }

            balance_sheet = stock.balance_sheet.to_dict() if hasattr(stock, 'balance_sheet') else {}
            latest_balance_sheet = balance_sheet.get(list(balance_sheet.keys())[0] if balance_sheet else {}, {})
            simplified_balance_sheet = {
                'totalAssets': latest_balance_sheet.get('Total Assets'),
                'totalLiabilities': latest_balance_sheet.get('Total Liabilities Net Minority Interest'),
                'commonStockEquity': latest_balance_sheet.get('Common Stock Equity')
            }

            cash_flow = stock.cashflow.to_dict() if hasattr(stock, 'cashflow') else {}
            latest_cash_flow = cash_flow.get(list(cash_flow.keys())[0] if cash_flow else {}, {})
            simplified_cash_flow = {
                'operatingCashFlow': latest_cash_flow.get('Operating Cash Flow'),
                'freeCashFlow': latest_cash_flow.get('Free Cash Flow')
            }
            return {
                "info": simplified_info,
                "historical_data": hist_trimmed,
                "financials": simplified_financials,
                "balance_sheet": simplified_balance_sheet,
                "cash_flow": simplified_cash_flow
            }

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return {"error": str(e)}

    def _is_valid_value(self, v: Any) -> bool:
        """Helper function to check if a value is valid (not empty or all NaN)."""
        if isinstance(v, (list, dict)):
            return bool(v)
        if pd.api.types.is_array_like(v):
            return not pd.isna(v).all()
        return not pd.isna(v)
    
    