"""
File I/O utilities and output formatting for the startpakket processing script.
"""
import logging
from typing import Dict, Any
import pandas as pd

from result_formatter import format_results

logger = logging.getLogger(__name__)


def save_results(results: Dict[str, Any], output_path: str) -> None:
    """
    Save results to file (auto-detect format based on extension).
    
    Args:
        results: Results dictionary (legacy or standardized format)
        output_path: Path to save the file (.csv or .xlsx)
    """
    # Convert to standardized format if needed
    if 'warnings' not in results:
        results = format_results(results)
    
    if output_path.lower().endswith('.csv'):
        _save_results_csv(results, output_path)
    elif output_path.lower().endswith('.xlsx'):
        _save_results_xlsx(results, output_path)
    else:
        raise ValueError(f"Unsupported output format: {output_path}. Use .csv or .xlsx")


def _save_results_csv(results: Dict[str, Any], output_path: str) -> None:
    """Save results to a CSV file."""
    try:
        if results['warnings']:
            df = pd.DataFrame(results['warnings'])
        else:
            df = pd.DataFrame(columns=['student_id', 'voornaam', 'achternaam', 'email', 'warning_type', 'waarschuwing'])
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Results saved to CSV: {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving results to CSV {output_path}: {e}")
        raise


def _save_results_xlsx(results: Dict[str, Any], output_path: str) -> None:
    """Save results to an Excel file with multiple sheets."""
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Summary
            summary_df = pd.DataFrame([results['summary']])
            summary_df.to_excel(writer, sheet_name='Samenvatting', index=False)
            
            # Sheet 2: All Warnings
            if results['warnings']:
                warnings_df = pd.DataFrame(results['warnings'])
                warnings_df.to_excel(writer, sheet_name='Alle Waarschuwingen', index=False)
                
                # Separate sheets per warning type
                for warning_type in ['FAIL_adviesrapport', 'SP_mismatch_predelib', 'SP_mismatch_dashboard']:
                    filtered = [w for w in results['warnings'] if w['warning_type'] == warning_type]
                    if filtered:
                        sheet_name = {
                            'FAIL_adviesrapport': 'FAIL Adviesrapport',
                            'SP_mismatch_predelib': 'SP Mismatch Predelib',
                            'SP_mismatch_dashboard': 'SP Mismatch Dashboard'
                        }[warning_type]
                        pd.DataFrame(filtered).to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"Results saved to Excel: {output_path}")
        
    except Exception as e:
        logger.error(f"Error saving results to Excel {output_path}: {e}")
        raise


def print_summary(results: Dict[str, Any]) -> None:
    """Print a summary of the results to console."""
    # Convert to standardized format if needed
    if 'warnings' not in results:
        results = format_results(results)
    
    summary = results['summary']
    warnings = results['warnings']
    
    print(f"\n{'='*60}")
    print("STARTPAKKET DT1 PROCESS SAMENVATTING")
    print(f"{'='*60}")
    print(f"Status: {results['status']}")
    print(f"Predeliberatie bestand: {summary['predelib_file']}")
    print(f"Dashboard bestand: {summary['dashboard_file']}")
    print(f"Predeliberatie records: {summary['predelib_records']}")
    print(f"Dashboard records: {summary['dashboard_records']}")
    print(f"\nTotaal waarschuwingen: {summary['total_warnings']}")
    print(f"  - FAIL adviesrapport: {summary['fail_adviesrapport_count']}")
    print(f"  - SP mismatch predelib: {summary['sp_mismatch_predelib_count']}")
    print(f"  - SP mismatch dashboard: {summary['sp_mismatch_dashboard_count']}")
    
    if warnings:
        print(f"\n{'-'*60}")
        print("GEDETAILLEERDE WAARSCHUWINGEN:")
        print(f"{'-'*60}")
        
        for warning in warnings:
            print(f"\n[{warning['warning_type']}] {warning['voornaam']} {warning['achternaam']} (ID: {warning['student_id']})")
            print(f"  Email: {warning['email']}")
            print(f"  Waarschuwing: {warning['waarschuwing']}")
    else:
        print("\n✅ Geen waarschuwingen gevonden!")
    
    print(f"{'='*60}")

def print_json_summary(results: Dict[str, Any]) -> None:
    """Print a JSON summary of the results to console."""
    import json
    
    # Convert to standardized format if needed
    if 'warnings' not in results:
        results = format_results(results)
    
    print("---UI_OUTPUT_START---")
    print(json.dumps(results, ensure_ascii=False))
    print("---UI_OUTPUT_END---")