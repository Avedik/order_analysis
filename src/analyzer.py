import logging
from pathlib import Path

import pandas as pd


class OrderAnalyzer:
	def __init__(
		self,
		data_dir: Path,
		log_dir: Path,
		reports_dir: Path,
		output_filename: str,
		status_column: str,
		delivered_status: str,
		log_filename: str = "errors.log",
	) -> None:
		self.data_dir = Path(data_dir)
		self.reports_dir = Path(reports_dir)
		self.output_filename = output_filename
		self.status_column = status_column
		self.delivered_status = delivered_status

		Path(log_dir).mkdir(parents=True, exist_ok=True)
		self.logger = logging.getLogger(f"{__name__}.{id(self)}")
		self.logger.setLevel(logging.ERROR)
		handler = logging.FileHandler(Path(log_dir) / log_filename, encoding="utf-8")
		handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
		self.logger.addHandler(handler)
		self.logger.propagate = False

	def load_file(self, file_path: Path) -> pd.DataFrame:
		file_path = Path(file_path)
		try:
			data = pd.read_csv(file_path)
			required_columns = {self.status_column, "total_amount"}
			missing_columns = required_columns - set(data.columns)
			if missing_columns:
				raise ValueError(f"missing columns: {', '.join(sorted(missing_columns))}")

			amounts = pd.to_numeric(data["total_amount"], errors="coerce")
			if amounts.isna().any():
				raise ValueError("column 'total_amount' contains non-numeric values")
			data["total_amount"] = amounts
			return data
		except (OSError, pd.errors.ParserError, ValueError) as error:
			self.logger.error("Could not load %s: %s", file_path.name, error)
			raise

	def filter_delivered_orders(self, data: pd.DataFrame) -> pd.DataFrame:
		return data[data[self.status_column] == self.delivered_status]

	def calculate_metrics(self, delivered_orders: pd.DataFrame, filename: str) -> dict:
		delivered_count = len(delivered_orders)
		total_amount = delivered_orders["total_amount"].sum()
		average_amount = delivered_orders["total_amount"].mean()
		return {
			"filename": filename,
			"delivered_orders": delivered_count,
			"total_delivered_amount": round(float(total_amount), 2),
			"average_delivered_amount": round(float(average_amount), 2)
			if delivered_count
			else 0.0,
		}

	def process_file(self, file_path: Path) -> dict | None:
		file_path = Path(file_path)
		try:
			data = self.load_file(file_path)
			delivered_orders = self.filter_delivered_orders(data)
			return self.calculate_metrics(delivered_orders, file_path.name)
		except (OSError, pd.errors.ParserError, ValueError):
			return None

	def process_all_files(self) -> pd.DataFrame:
		results = []
		for file_path in sorted(self.data_dir.glob("*.csv")):
			result = self.process_file(file_path)
			if result is not None:
				results.append(result)

		report = pd.DataFrame(
			results,
			columns=[
				"filename",
				"delivered_orders",
				"total_delivered_amount",
				"average_delivered_amount",
			],
		)
		self.reports_dir.mkdir(parents=True, exist_ok=True)
		report.to_csv(self.reports_dir / self.output_filename, index=False)
		return report
