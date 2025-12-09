import pandas as pd
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('predelib_processing.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_students_with_fail_adviesrapport(predelib_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check for students with 'FAIL' in 'Adviesrapport code' column and extract their details.
    
    Args:
        predelib_df (pandas.DataFrame): Processed predeliberation dataframe
    
    Returns:
        list: List of dictionaries containing failed student details
        
    Raises:
        ValueError: If input dataframe is invalid
        KeyError: If required columns are missing
    """
    logger.info("Starting failed students check")
    
    try:
        # Validate input dataframe
        if predelib_df is None or predelib_df.empty:
            error_msg = "Predelib dataframe is None or empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Predelib dataframe shape: {predelib_df.shape}")
        
        # Define required columns
        required_columns = [
            'ID', 'Achternaam', 'Voornaam', 'E-mail', 
            'Totaal aantal SP', 'Aantal SP vereist', 'Waarschuwing', 'Adviesrapport code'
        ]
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in predelib_df.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns in predelib dataframe: {missing_columns}"
            logger.error(error_msg)
            logger.info(f"Available columns: {list(predelib_df.columns)}")
            raise KeyError(error_msg)
        
        logger.info("All required columns found in dataframe")
        
        # Debug Adviesrapport code column
        logger.debug(f"Adviesrapport code column type: {predelib_df['Adviesrapport code'].dtype}")
        unique_codes = predelib_df['Adviesrapport code'].unique()
        logger.debug(f"Unique Adviesrapport codes: {unique_codes}")
        
        # Filter for FAIL cases
        try:
            # Convert to string and check for FAIL (case-insensitive)
            fail_mask = predelib_df['Adviesrapport code'].astype(str).str.upper() == 'FAIL'
            students_with_fail_ar_df = predelib_df[fail_mask].copy()
            
            logger.info(f"Found {len(students_with_fail_ar_df)} students with FAIL status")
            
            # Remove duplicate rows (exact same values in all columns)
            initial_count = len(students_with_fail_ar_df)
            students_with_fail_ar_df = students_with_fail_ar_df.drop_duplicates(subset=['ID'])
            final_count = len(students_with_fail_ar_df)
            
            duplicates_removed = initial_count - final_count
            if duplicates_removed > 0:
                logger.info(f"Removed {duplicates_removed} duplicate rows")
            else:
                logger.info("No duplicate rows found")
            
            logger.info(f"Final count after duplicate removal: {final_count} students with FAIL status")
            
        except Exception as e:
            error_msg = f"Error filtering for FAIL status: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if len(students_with_fail_ar_df) == 0:
            logger.info("No students with FAIL status found")
            return []
        
        # Extract details for failed students
        students_with_fail_ar = []
        processed_count = 0
        
        for index, row in students_with_fail_ar_df.iterrows():
            try:
                # Extract student details
                student_details = {
                    'ID': row['ID'],
                    'Achternaam': row['Achternaam'],
                    'Voornaam': row['Voornaam'],
                    'E-mail': row['E-mail'],
                    'Totaal_aantal_SP': row['Totaal aantal SP'],
                    'Aantal_SP_vereist': row['Aantal SP vereist'],
                    'Waarschuwing': row['Waarschuwing'],
                    'Adviesrapport_code': row['Adviesrapport code']
                }
                
                # Handle potential NaN values
                for key, value in student_details.items():
                    if pd.isna(value):
                        student_details[key] = None
                        logger.warning(f"NaN value found for {key} in student ID: {row['ID']}")
                
                students_with_fail_ar.append(student_details)
                processed_count += 1
                
                logger.debug(f"Processed failed student: ID={row['ID']}, "
                           f"Name={row['Achternaam']}, {row['Voornaam']}")
                
            except Exception as e:
                logger.error(f"Error processing student at index {index}: {e}")
                continue
        
        logger.info(f"Successfully processed {processed_count} failed students")
        
        # Log summary
        if students_with_fail_ar:
            logger.warning(f"Found {len(students_with_fail_ar)} students with FAIL status")
            for student in students_with_fail_ar:
                logger.info(f"Failed student - ID: {student['ID']}, "
                          f"Name: {student['Achternaam']}, {student['Voornaam']}, "
                          f"SP: {student['Totaal_aantal_SP']}/{student['Aantal_SP_vereist']}")
        else:
            logger.info("No failed students found")
        
        return students_with_fail_ar
        
    except Exception as e:
        logger.error(f"Unexpected error in check_students_with_fail_ar: {e}")
        raise

def check_students_with_mismatching_SP_values(predelib_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Check for students with mismatching SP values in the predeliberation dataframe.
    
    Args:
        predelib_df (pandas.DataFrame): Processed predeliberation dataframe
    
    Returns:
        list: List of dictionaries containing student details with mismatching SP values
    """
    logger.info("Starting check for students with mismatching SP values in the predeliberation file")
    try:
        # Validate input dataframe
        if predelib_df is None or predelib_df.empty:
            error_msg = "Predelib dataframe is None or empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Predelib dataframe shape: {predelib_df.shape}")
        
        # Define required columns
        required_columns = [
            'ID', 'Achternaam', 'Voornaam', 'E-mail', 
            'Totaal aantal SP', 'Aantal SP vereist'
        ]
        
        # Check for required columns
        missing_columns = [col for col in required_columns if col not in predelib_df.columns]
        
        if missing_columns:
            error_msg = f"Missing required columns in predelib dataframe: {missing_columns}"
            logger.error(error_msg)
            logger.info(f"Available columns: {list(predelib_df.columns)}")
            raise KeyError(error_msg)
        
        logger.info("All required columns found in dataframe")

        # Use vectorized comparison to find rows where the SP values differ
        sp_col = predelib_df['Totaal aantal SP']
        req_col = predelib_df['Aantal SP vereist']

        # Simple inequality works for most cases; NaN != NaN will be True which is acceptable
        mask = sp_col != req_col
        mismatches_df = predelib_df[mask].copy()

        logger.info(f"Found {len(mismatches_df)} raw rows with mismatching SP values")

        if mismatches_df.empty:
            logger.info("No students with mismatching SP values found")
            return []

        # Keep only unique students by 'ID' (first occurrence).
        if 'ID' in mismatches_df.columns:
            before_dedup = len(mismatches_df)
            mismatches_df = mismatches_df.drop_duplicates(subset=['ID'])
            after_dedup = len(mismatches_df)
            logger.info(f"Reduced from {before_dedup} rows to {after_dedup} unique students by ID")
        else:
            logger.warning("Column 'ID' not found - cannot deduplicate by student ID")

        # Ensure optional columns exist to avoid KeyError when building dicts
        for optional_col in ('Waarschuwing', 'Adviesrapport code'):
            if optional_col not in mismatches_df.columns:
                mismatches_df[optional_col] = None

        # Build the list of mismatching students
        mismatching_students = []
        for _, row in mismatches_df.iterrows():
            mismatching_students.append({
                'ID': row.get('ID'),
                'Achternaam': row.get('Achternaam'),
                'Voornaam': row.get('Voornaam'),
                'E-mail': row.get('E-mail'),
                'Totaal_aantal_SP': row.get('Totaal aantal SP'),
                'Aantal_SP_vereist': row.get('Aantal SP vereist'),
                'Waarschuwing': row.get('Waarschuwing'),
                'Adviesrapport_code': row.get('Adviesrapport code')
            })

        logger.info(f"Returning {len(mismatching_students)} unique students with mismatching SP values")
        return mismatching_students

    except Exception as e:
        logger.error(f"Unexpected error in check_students_with_mismatching_SP_values: {e}")
        raise


def print_students_with_fail_ar_summary(students_with_fail_ar: List[Dict[str, Any]], predelib_df: pd.DataFrame):
    """Print a formatted summary of students with FAIL status"""
    print(f"\n{'='*80}")
    print("Students with FAIL AR status report")
    print(f"{'='*80}")
    print(f"Total students processed: {len(predelib_df)}")
    print(f"Students with FAIL status: {len(students_with_fail_ar)}")
    
    if students_with_fail_ar:
        print(f"\nDetailed failed students list:")
        print(f"{'ID':<10} {'Name':<25} {'Email':<30} {'SP':<15} {'Warning':<20}")
        print(f"{'-'*10} {'-'*25} {'-'*30} {'-'*15} {'-'*20}")
        
        for student in students_with_fail_ar:
            name = f"{student['Achternaam']}, {student['Voornaam']}"
            sp_info = f"{student['Totaal_aantal_SP']}/{student['Aantal_SP_vereist']}"
            warning = str(student['Waarschuwing']) if student['Waarschuwing'] else "None"
            
            print(f"{str(student['ID']):<10} {name[:25]:<25} {str(student['E-mail'])[:30]:<30} "
                  f"{sp_info:<15} {warning[:20]:<20}")
    else:
        print("\n✅ No students with FAIL status found!")
    
    print(f"{'='*80}")


if __name__ == "__main__":
    # Example usage - can be used for testing
    logger.info("Starting failed students check script")
    
    try:
        from checkheaders import check_headers_predelibfile
        
        # Read the Excel file
        logger.info("Reading predelib Excel file")
        try:
            df_predelib = pd.read_excel('db.xlsx')
            logger.info(f"Successfully loaded predelib file with shape: {df_predelib.shape}")
        except FileNotFoundError:
            logger.error("db.xlsx file not found")
            raise
        except Exception as e:
            logger.error(f"Error reading db.xlsx: {e}")
            raise
        
        # Process the dataframe
        logger.info("Processing predelib dataframe")
        try:
            processed_predelib_df = check_headers_predelibfile(df_predelib)
            logger.info(f"Processed predelib dataframe shape: {processed_predelib_df.shape}")
        except Exception as e:
            logger.error(f"Error processing predelib file: {e}")
            raise
        
        # Check for failed students
        logger.info("Checking for failed students")
        try:
            students_with_fail_ar = check_students_with_fail_adviesrapport(processed_predelib_df)
            logger.info(f"Failed students check completed. Found {len(students_with_fail_ar)} failed students.")
            
            # Print summary for console output
            print_students_with_fail_ar_summary(students_with_fail_ar, processed_predelib_df)
            
        except Exception as e:
            logger.error(f"Error during failed students check: {e}")
            raise
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print("Error: Could not import required modules. Make sure checkheaders.py is in the same directory.")
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        print(f"An error occurred: {e}")
        print("Check the log file 'predelib_processing.log' for detailed error information.")
    finally:
        logger.info("Failed students check script completed")