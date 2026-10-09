# MP1 Data Pipeline

A configurable command-line pipeline that loads a data file, checks it against a
schema, cleans it, and writes the result as CSV.

## What it does

The pipeline takes three paths on the command line — an input data file, a YAML
configuration file, and an output path — and moves the data through four stages.
It first validates that both input paths exist, then loads the data file and the
configuration, choosing a loader from the file extension so CSV, JSON, and YAML
inputs are all handled by the same call. The loaded DataFrame is validated
against the schema named in the configuration: a missing required column is
fatal, while individual values that cannot be read as numbers are dropped with a
warning so one malformed cell does not end the run. The surviving data is then
cleaned in a fixed order — duplicate rows, then rows with missing values, then
statistical outliers — with each step applied only if the configuration enables
it. Finally the cleaned DataFrame is written to the output path, creating the
output directory if it does not yet exist, and a report summarising how many rows
and columns were removed is printed. Because every column name, threshold, and
on/off switch lives in `config/config.yaml`, pointing the pipeline at a different
dataset means editing configuration and command-line paths, not Python.

## Layout

| Path | Responsibility |
| ---- | -------------- |
| `pipeline.py` | Entry point. Parses arguments and coordinates the stages below. |
| `src/utils.py` | Logging configuration and input-path validation. |
| `src/data_loaders.py` | Reads CSV, JSON, and YAML files, dispatching on file extension. |
| `src/data_validator.py` | Enforces required columns and numeric types. |
| `src/data_processor.py` | Removes duplicates, missing values, and outliers; builds the cleaning report. |
| `src/data_output.py` | Writes the cleaned DataFrame to CSV. |
| `config/config.yaml` | Controls which checks and cleaning steps run, and on which columns. |
| `fixtures/` | Small sample files for testing. |
| `output/` | Generated results. Not committed. |

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

## Running it

```bash
python pipeline.py --input fixtures/sample_data.csv --output output/clean.csv --config config/config.yaml --verbose
```

Output:

```text
00:02:40 DEBUG    __main__ — Arguments parsed: input=fixtures/sample_data.csv, output=output/clean.csv, config=config/config.yaml
00:02:40 INFO     src.utils — Input file validated: fixtures/sample_data.csv
00:02:40 INFO     src.utils — Input file validated: config/config.yaml
00:02:40 INFO     src.data_loaders — Loaded CSV file: fixtures/sample_data.csv (100 rows)
00:02:40 INFO     src.data_loaders — Loaded YAML file: config/config.yaml
00:02:40 WARNING  src.data_validator — Removed 2 rows with invalid numeric values in rating
00:02:40 DEBUG    src.data_validator — Validation: 100 → 98 rows
00:02:40 INFO     __main__ — Validation complete: 100 → 98 rows
00:02:40 DEBUG    src.data_processor — remove_duplicates: 98 → 96 rows
00:02:40 DEBUG    src.data_processor — handle_missing: 96 → 94 rows
00:02:40 DEBUG    src.data_processor — rating: method=iqr, threshold=1.5, lower=1.4, upper=6.2, removed=2
00:02:40 INFO     __main__ — Processing complete: 98 → 92 rows
00:02:40 DEBUG    src.data_output — Saved 92 rows to output/clean.csv
00:02:40 INFO     __main__ — Saved cleaned data to output/clean.csv

Cleaning report:
{'rows_before': 98, 'rows_after': 92, 'rows_removed': 6, 'columns_before': 5, 'columns_after': 5, 'columns_removed': 0}
```

Drop `--verbose` to see only the `INFO` lines. The pipeline exits with status `1`
if an input path is missing, a file extension is unsupported, a required column
is absent, or the configuration names an unsupported outlier method or axis.

## Arguments

| Argument | Required | Description |
| -------- | -------- | ----------- |
| `--input`, `-i` | Yes | Path to the input data file (`.csv`, `.json`, or `.yaml`). |
| `--config` | Yes | Path to the YAML configuration file. |
| `--output`, `-o` | Yes | Path for the cleaned CSV. Parent directories are created. |
| `--verbose`, `-v` | No | Show `DEBUG` messages from each module. |
