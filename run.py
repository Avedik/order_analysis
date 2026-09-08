import config
from src.analyzer import OrderAnalyzer


def main() -> None:
	analyzer = OrderAnalyzer(
		data_dir=config.DATA_DIR,
		log_dir=config.LOG_DIR,
		reports_dir=config.REPORTS_DIR,
		output_filename=config.OUTPUT_FILENAME,
		status_column=config.STATUS_COLUMN,
		delivered_status=config.DELIVERED_STATUS,
		log_filename=config.LOG_FILENAME,
	)
	report = analyzer.process_all_files()
	print(report.to_string(index=False))


if __name__ == "__main__":
	main()
