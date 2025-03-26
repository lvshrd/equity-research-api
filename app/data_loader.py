# app/data_loader.py
import json
from pathlib import Path
from typing import Dict, Any
import toml

class DataLoader:
    def __init__(self):
        self.data_path = Path(toml.load("config.toml")["DATA"]["DATA_PATH"])
        self.company_metadata = self._load_metadata()
        self.valid_company_ids = set(self.company_metadata.keys())

    def _load_metadata(self) -> Dict[str, Any]:
        """Load company metadata from JSON file"""
        try:
            with open(self.data_path / "company_metadata.json") as f:
                return {item["company_id"]: item for item in json.load(f)}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load metadata: {str(e)}")

    def validate_company(self, company_id: str) -> bool:
        """Check if company exists in metadata"""
        return company_id in self.valid_company_ids

    def get_company_data(self, company_id: str) -> Dict[str, Any]:
        """Get combined data for report generation"""
        if not self.validate_company(company_id):
            raise ValueError("Invalid company ID")
            
        return {
            "metadata": self.company_metadata[company_id],
            # Add other data sources here later
        }

# Singleton instance
data_loader = DataLoader()