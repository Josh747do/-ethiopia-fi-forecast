"""
Configuration settings for Ethiopia Financial Inclusion Forecasting System.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
MODELS_DIR = PROJECT_ROOT / "models"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, 
                  REPORTS_DIR, FIGURES_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data URLs (from challenge document)
DATA_URLS = {
    "unified_data": "https://docs.google.com/spreadsheets/d/1yzVpRe8jLA2JOEHwB62Z7_B0vjLiY95zA23eTJfmQtM/export?format=csv",
    "reference_codes": "https://docs.google.com/spreadsheets/d/1eHmiaESHKsXyFSExay6VrLgNh_y5W5f0czn9x0spQDE/export?format=csv",
    "additional_data": "https://docs.google.com/spreadsheets/d/1mosiu40PUV-pq-yVFZdVFWt9fQ0A0jlw/export?format=csv"
}

# Key indicators from Global Findex
INDICATORS = {
    "ACCESS": {
        "code": "ACC_OWNERSHIP",
        "name": "Account Ownership Rate",
        "definition": "The share of adults (age 15+) who report having an account at a financial institution or using mobile money"
    },
    "USAGE": {
        "code": "USG_DIGITAL_PAYMENT",
        "name": "Digital Payment Adoption Rate",
        "definition": "The share of adults who report using digital payments in the past 12 months"
    }
}

# Ethiopia-specific constants
ETHIOPIA_POPULATION_2024 = 126_000_000  # Approximate
ADULT_POPULATION_RATIO = 0.6  # 60% of population is 15+ (estimate)

# Event categories
EVENT_CATEGORIES = [
    "policy",
    "product_launch",
    "infrastructure",
    "market_entry",
    "milestone",
    "partnership",
    "regulation"
]

# Pillars
PILLARS = ["access", "usage", "quality", "welfare"]

# Model settings
RANDOM_SEED = int(os.getenv("RANDOM_SEED", 42))
FORECAST_YEARS = [2025, 2026, 2027]
HISTORICAL_START_YEAR = 2011
HISTORICAL_END_YEAR = 2024

# Dashboard settings
DASHBOARD_TITLE = "Ethiopia Financial Inclusion Forecasting System"
DASHBOARD_DESCRIPTION = "Track and forecast Ethiopia's progress on financial inclusion"