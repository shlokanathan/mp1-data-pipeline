"""Data Processing Pipeline

DS 3500 - MP1

Usage:
    python pipeline.py --input data.csv --output clean.csv --config config.yaml
    python pipeline.py --input data.csv --output clean.csv --config config.yaml --verbose
"""

import argparse
import logging
import sys
from pathlib import Path

from data_loaders import load_data
from data_processor import process_data, create_cleaning_report


logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Data processing pipeline")

    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to the input file"
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to the YAML configuration file"
    )

    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Path to the output file"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()


def main():
    """Main pipeline function."""
    args = parse_arguments()
    setup_logging(args.verbose)

    logger.debug(
        f"Arguments parsed: input={args.input}, output={args.output}, "
        f"config={args.config}"
    )

    if not validate_input(args.input):
        sys.exit(1)

    if not validate_input(args.config):
        sys.exit(1)

    try:
        data = load_data(args.input)
        config = load_data(args.config)
    except ValueError:
        sys.exit(1)

    original = data.copy()

    try:
        data = process_data(data, config)
    except ValueError:
        sys.exit(1)

    report = create_cleaning_report(original, data)
    print(report)
    logger.info(
        f"Processing complete: {report['rows_before']} → {report['rows_after']} rows"
    )

    data.to_csv(args.output, index=False)
    logger.info(f"Saved cleaned data to {args.output}")


if __name__ == "__main__":
    main()
