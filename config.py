from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
LOG_FILENAME = "errors.log"
OUTPUT_FILENAME = "summary_report.csv"
STATUS_COLUMN = "status"
DELIVERED_STATUS = "Delivered"
