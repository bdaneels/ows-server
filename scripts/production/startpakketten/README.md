# Startpakket Processing Tool

A Python tool for processing and comparing student data from predeliberation and dashboard Excel files. The tool identifies students with FAIL status and compares SP (study points) values between different data sources.

## Project Structure

The codebase has been organized into focused modules:

### Core Scripts

- **`script.py`** - Main orchestration script, handles command-line interface and coordinates all processing
- **`data_processor.py`** - Core data processing functions for Excel file handling
- **`cli_args.py`** - Command-line argument parsing and validation
- **`config.py`** - Configuration management and logging setup
- **`file_utils.py`** - File I/O utilities and output formatting

### Processing Modules

- **`checkheaders.py`** - Excel file header processing and normalization
- **`process_predelib_file.py`** - Predeliberation file analysis and FAIL status detection
- **`compare_sp.py`** - SP value comparison between predeliberation and dashboard files

## Usage

### Basic Usage

```bash
python script.py --predelib db.xlsx --dashboard dashboard_inschrijvingen.xlsx
```

### Advanced Usage

```bash
# Save results to JSON file
python script.py -p db.xlsx -d dashboard_inschrijvingen.xlsx --output results.json

# Enable verbose logging
python script.py db.xlsx dashboard_inschrijvingen.xlsx results.xlsx --verbose

# Custom log file
python script.py --predelib db.xlsx --dashboard dashboard_inschrijvingen.xlsx --log-file custom.log
```

### Command-line Options

- `--predelib, -p`: Path to predeliberation Excel file (required)
- `--dashboard, -d`: Path to dashboard Excel file (required)
- `--output, -o`: Output file path for JSON results (optional)
- `--verbose, -v`: Enable verbose logging
- `--log-file`: Custom log file path (default: startpakket_processing.log)

## Features

1. **File Validation**: Automatically validates that input files exist and are Excel format
2. **Header Processing**: Intelligently detects and normalizes Excel headers
3. **FAIL Detection**: Identifies students with FAIL status in adviesrapport code
4. **SP Comparison**: Compares study points between predeliberation and dashboard data
5. **Comprehensive Logging**: Detailed logging with configurable verbosity
6. **Flexible Output**: Console summary with optional JSON export
7. **Error Handling**: Robust error handling with appropriate exit codes

## Installation

1. Ensure Python 3.12+ is installed
2. Install required dependencies:
   ```bash
   pip install pandas openpyxl
   ```

## Input File Requirements

### Predeliberation File (db.xlsx)

Must contain columns:

- ID, Achternaam, Voornaam, E-mail
- Totaal aantal SP, Aantal SP vereist
- Adviesrapport code, Waarschuwing

### Dashboard File (dashboard_inschrijvingen.xlsx)

Must contain columns:

- ID, Naam, Voornaam
- Ingeschr. SP (intern)

## Output

The tool provides:

1. **Console Summary**: Overview of processing results
2. **Failed Students Report**: Detailed list of students with FAIL status
3. **SP Mismatch Report**: Any discrepancies between predeliberation and dashboard SP values
4. **Optional JSON Export**: Machine-readable results for further processing

## Exit Codes

- `0`: Success (no mismatches found)
- `1`: Processing completed but mismatches found
- `130`: Process interrupted by user
- Other: Fatal error occurred

## Logging

All processing activities are logged to `startpakket_processing.log` by default. Use `--verbose` for detailed debug information.
