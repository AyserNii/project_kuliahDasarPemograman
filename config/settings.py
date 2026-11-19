import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Storage Paths
STORAGE_DIR = BASE_DIR / "storage"
IMPORTS_DIR = STORAGE_DIR / "imports"
EXPORTS_DIR = STORAGE_DIR / "exports"
EXPORT_REPORTS_DIR = EXPORTS_DIR / "reports"
EXPORT_BACKUPS_DIR = EXPORTS_DIR / "backups"

# Output Paths
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_REPORTS_DIR = OUTPUT_DIR / "reports"
OUTPUT_CHARTS_DIR = OUTPUT_DIR / "charts"

# Ensure runtime directories exist
for path in [
    IMPORTS_DIR,
    EXPORT_REPORTS_DIR,
    EXPORT_BACKUPS_DIR,
    OUTPUT_REPORTS_DIR,
    OUTPUT_CHARTS_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)

# Default Business Parameters
DEFAULT_ANNUAL_DAYS = 365
DEFAULT_LEAD_TIME_DAYS = 5.0
DEFAULT_ORDERING_COST = 50000.0  # Rp 50.000 per order
DEFAULT_HOLDING_COST_RATE = 0.20  # 20% of unit cost per year
DEFAULT_SERVICE_LEVEL_Z = 1.65  # ~95% service level
