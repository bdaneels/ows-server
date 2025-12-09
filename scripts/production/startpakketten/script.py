"""
Main script for processing and comparing student data from predeliberation and dashboard Excel files.

"""
import sys
import logging

from cli_args import parse_arguments
from config import setup_logging, get_exit_code
from data_processor import process_files
from file_utils import save_results, print_summary, print_json_summary


def main():
    """Main function - orchestrates the entire processing pipeline"""
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Set up logging configuration
        logger = setup_logging(args.log_file, args.verbose)
        
        logger.info("Starting startpakket processing")
        logger.info(f"Predelib file: {args.predelib}")
        logger.info(f"Dashboard file: {args.dashboard}")
        
        # Process the Excel files
        results = process_files(args.predelib, args.dashboard, args.verbose)
        
        # Save results to file if specified
        if args.output:
            save_results(results, args.output)
        
        # Print summary to console
        print_summary(results)
        print_json_summary(results)
        
        # Exit with appropriate code
        exit_code = get_exit_code(results)
        logger.info(f"Processing completed with exit code: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\nProcessing interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
