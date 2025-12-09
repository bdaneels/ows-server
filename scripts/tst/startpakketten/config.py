"""
Configuration and logging setup for the startpakket processing application.
"""
import logging
import sys
from typing import Optional


def setup_logging(log_file: str = 'startpakket_processing.log', verbose: bool = False) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_file: Path to the log file
        verbose: Enable debug logging if True
        
    Returns:
        Configured logger instance
    """
    # Remove existing handlers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Set logging level
    level = logging.DEBUG if verbose else logging.INFO
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    
    if verbose:
        logger.debug("Verbose logging enabled")
    
    return logger


def get_exit_code(results: dict) -> int:
    """
    Determine the appropriate exit code based on processing results.
    
    Args:
        results: Processing results dictionary
        
    Returns:
        Exit code (0 for success, 1 for mismatches found)
    """
    return 0 if results.get('mismatches_count', 0) == 0 else 1
