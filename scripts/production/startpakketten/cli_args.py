"""
Command-line argument parsing for the startpakket processing script.
"""
import argparse
import os


def validate_file_path(file_path: str) -> str:
    """Validate that the file exists and is an Excel file"""
    if not os.path.exists(file_path):
        raise argparse.ArgumentTypeError(f"File '{file_path}' does not exist")
    
    if not file_path.lower().endswith(('.xlsx', '.xls')):
        raise argparse.ArgumentTypeError(f"File '{file_path}' is not an Excel file (.xlsx or .xls)")
    
    return file_path


def validate_output_path(file_path: str) -> str:
    """Validate that the output file has .xlsx or .csv extension"""
    if not file_path.lower().endswith(('.xlsx', '.csv')):
        raise argparse.ArgumentTypeError(f"Output file '{file_path}' must have .xlsx or .csv extension")
    
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        raise argparse.ArgumentTypeError(f"Directory '{dir_path}' does not exist")
    
    return file_path


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Process and compare student data from predeliberation and dashboard Excel files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s db.xlsx dashboard_inschrijvingen.xlsx
  %(prog)s db.xlsx dashboard.xlsx output.xlsx
  %(prog)s db.xlsx dashboard.xlsx results.csv --verbose
        """
    )
    
    parser.add_argument(
        'predelib',
        type=validate_file_path,
        help='Path to the predeliberation Excel file'
    )
    
    parser.add_argument(
        'dashboard',
        type=validate_file_path,
        help='Path to the dashboard Excel file'
    )
    
    parser.add_argument(
        'output',
        nargs='?',
        default=None,
        type=validate_output_path,
        help='Output file path (.xlsx or .csv)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        default='startpakket_processing.log',
        help='Path to log file'
    )
    
    return parser.parse_args()