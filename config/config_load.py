# config/config_load.py
import toml
from pathlib import Path
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """Load configuration from TOML file"""
    config_path = Path(__file__).parent / "config.toml"
    try:
        with open(config_path, "r") as f:
            return toml.load(f)
    except FileNotFoundError:
        raise RuntimeError("config.toml not found in project root")

# Global configuration object
CONFIG = load_config()