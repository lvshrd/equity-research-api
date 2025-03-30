# app/data_loader.py
import json
from pathlib import Path
from typing import Dict, Any, List
from config.config_load import CONFIG

class DataLoader:
    def __init__(self):
        self.data_path = Path(CONFIG["app"]["data_path"])
        self.company_metadata = self._load_metadata()
        self.financial_data = self._load_financial_data()
        self.valid_company_ids = set(self.company_metadata.keys())

    def _load_metadata(self) -> Dict[str, Any]:
        """Load company metadata from JSON file"""
        try:
            with open(self.data_path / "company_metadata.json") as f:
                return {str(item["company_id"]): item for item in json.load(f)}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load metadata: {str(e)}")

    def _load_financial_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load company financial data from JSON file"""
        try:
            with open(self.data_path / "company_financial_ratios.json") as f:
                data = json.load(f)
                
                result = {}
                for item in data:
                    company_id = str(item["company_id"])
                    if company_id not in result:
                        result[company_id] = []
                    result[company_id].append(item)
                return result
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load financial data: {str(e)}")

    def validate_company(self, company_id: str) -> bool:
        """Check if company exists in metadata"""
        return company_id in self.valid_company_ids

    def get_company_data(self, company_id: str) -> Dict[str, Any]:
        """Get combined data for report generation"""
        if not self.validate_company(company_id):
            raise ValueError("Invalid company ID")
        metadata = self.company_metadata[company_id]
        if "ticker" in metadata and isinstance(metadata["ticker"], str):
            metadata["ticker"] = metadata["ticker"].split(" ")[0]

        financial_data = self.financial_data.get(company_id, [])
        recent_years = sorted(list(set(item['fiscal_year'] for item in financial_data)), reverse=True)[:5]

        simplified_financial_data = []
        for item in financial_data:
            if item['fiscal_year'] in recent_years:
                simplified_financial_data.append({
                    'fiscal_year': item['fiscal_year'],
                    'total_revenue': item.get('total_revenue'),
                    'net_income': item.get('net_income'),
                    'shareholders_equity': item.get('shareholders_equity'),
                    'total_asset': item.get('total_asset'),
                    'total_liab': item.get('total_liab'),
                    'cash_and_cash_equivalents': item.get('cash_and_cash_equivalents'),
                    'long_term_debt': item.get('long_term_debt'),
                    'shares_outstanding': item.get('shares_outstanding')
                })

        return {
            "metadata": metadata,
            "financial_data": simplified_financial_data
        }

# Singleton instance
data_loader = DataLoader()