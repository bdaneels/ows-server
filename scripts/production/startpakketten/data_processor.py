"""
Core data processing functions for the startpakket processing script.
"""
import pandas as pd
import logging
from typing import Dict, Any, List

from checkheaders import check_headers_dashboard_inschrijvingenfile, check_headers_predelibfile
from process_predelib_file import check_students_with_fail_adviesrapport, check_students_with_mismatching_SP_values
from compare_sp import compare_sp_values

logger = logging.getLogger(__name__)


def process_files(predelib_path: str, dashboard_path: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Process the Excel files and return results.
    
    Args:
        predelib_path: Path to the predeliberation Excel file
        dashboard_path: Path to the dashboard Excel file  
        verbose: Enable verbose logging
        
    Returns:
        Dictionary containing processing results
        
    Raises:
        Exception: If file processing fails
    """
    try:
        # Read Excel files
        logger.info(f"Reading predeliberation file: {predelib_path}")
        df_predelib = pd.read_excel(predelib_path)
        logger.info(f"Predelib file loaded successfully. Shape: {df_predelib.shape}")
        
        logger.info(f"Reading dashboard file: {dashboard_path}")
        df_dashboard = pd.read_excel(dashboard_path)
        logger.info(f"Dashboard file loaded successfully. Shape: {df_dashboard.shape}")
        
        # Process the dataframes
        logger.info("Processing predeliberation file headers")
        processed_predelib_df = check_headers_predelibfile(df_predelib)
        
        logger.info("Processing dashboard file headers")
        processed_dashboard_df = check_headers_dashboard_inschrijvingenfile(df_dashboard)

        # Check the predeliberation file for students with a fail in 'Adviesrapport code'
        logger.info("Checking for students with FAIL status in predeliberation file")
        students_with_fail = check_students_with_fail_adviesrapport(processed_predelib_df)
        students_with_mismatching_SP_values_predelib = check_students_with_mismatching_SP_values(processed_predelib_df)

        # Compare SP values
        logger.info("Comparing SP values between files")
        mismatches = compare_sp_values(processed_predelib_df, processed_dashboard_df)
        
        # Prepare results
        results = {
            'predelib_file': predelib_path,
            'dashboard_file': dashboard_path,
            'predelib_records': len(processed_predelib_df),
            'dashboard_records': len(processed_dashboard_df),
            'students_with_fail_count': len(students_with_fail),
            'students_with_fail': students_with_fail,
            'students_with_mismatching_SP_values_predelib_count': len(students_with_mismatching_SP_values_predelib),
            'students_with_mismatching_SP_values_predelib': students_with_mismatching_SP_values_predelib,
            'mismatches_count': len(mismatches),
            'mismatches': mismatches,
            'status': 'completed'
        }
        
        logger.info(f"Processing completed successfully.")
        return results
        
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        raise
