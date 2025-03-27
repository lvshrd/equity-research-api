# app/data_loader.py
import json
from pathlib import Path
from typing import Dict, Any, List
from config import CONFIG

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
            
        return {
            "metadata": self.company_metadata[company_id],
            "financial_data": self.financial_data.get(company_id, [])
        }

# Singleton instance
data_loader = DataLoader()