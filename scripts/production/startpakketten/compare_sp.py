import pandas as pd
import logging
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sp_comparison.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def compare_sp_values(predelib_df: pd.DataFrame, dashboard_df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Compare 'Totaal aantal SP' from predelib_df with 'Ingeschr. SP (intern)' from dashboard_df
    for matching IDs between the two dataframes.
    
    Args:
        predelib_df (pandas.DataFrame): Dataframe from predeliberation file with 'ID' and 'Totaal aantal SP' columns
        dashboard_df (pandas.DataFrame): Dataframe from dashboard file with 'ID' and 'Ingeschr. SP (intern)' columns
    
    Returns:
        list: List of dictionaries containing mismatches, or empty list if all match
        
    Raises:
        ValueError: If input dataframes are invalid
        KeyError: If required columns are missing
    """
    logger.info("Starting SP values comparison")
    
    try:
        # Validate input dataframes
        if predelib_df is None or predelib_df.empty:
            error_msg = "Predelib dataframe is None or empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if dashboard_df is None or dashboard_df.empty:
            error_msg = "Dashboard dataframe is None or empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check for required columns
        required_predelib_columns = ['ID', 'Totaal aantal SP']
        required_dashboard_columns = ['ID', 'Ingeschr. SP (intern)']
        
        missing_predelib_cols = [col for col in required_predelib_columns if col not in predelib_df.columns]
        missing_dashboard_cols = [col for col in required_dashboard_columns if col not in dashboard_df.columns]
        
        if missing_predelib_cols:
            error_msg = f"Missing required columns in predelib dataframe: {missing_predelib_cols}"
            logger.error(error_msg)
            raise KeyError(error_msg)
            
        if missing_dashboard_cols:
            error_msg = f"Missing required columns in dashboard dataframe: {missing_dashboard_cols}"
            logger.error(error_msg)
            raise KeyError(error_msg)
        
        logger.info("All required columns found in both dataframes")
        
        # Debug ID columns
        logger.debug(f"Predelib ID column type: {predelib_df['ID'].dtype}")
        logger.debug(f"Dashboard ID column type: {dashboard_df['ID'].dtype}")
        logger.debug(f"Sample predelib IDs: {list(predelib_df['ID'].head())}")
        logger.debug(f"Sample dashboard IDs: {list(dashboard_df['ID'].head())}")
        
        # Convert IDs to strings to ensure consistent comparison
        try:
            predelib_ids = set(str(x) for x in predelib_df['ID'] if pd.notna(x))
            dashboard_ids = set(str(x) for x in dashboard_df['ID'] if pd.notna(x))
        except Exception as e:
            error_msg = f"Error converting IDs to strings: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        matching_ids = predelib_ids.intersection(dashboard_ids)
        logger.info(f"Found {len(matching_ids)} matching IDs between the two dataframes")
        logger.info(f"Total predelib IDs: {len(predelib_ids)}")
        logger.info(f"Total dashboard IDs: {len(dashboard_ids)}")
        
        if len(matching_ids) == 0:
            logger.warning("No matching IDs found between the dataframes")
            return []
        
        # Compare SP values for matching IDs
        mismatches = []
        processed_count = 0
        
        for id_val in matching_ids:
            try:
                # Convert back to original type for filtering
                predelib_matches = predelib_df[predelib_df['ID'].astype(str) == id_val]
                dashboard_matches = dashboard_df[dashboard_df['ID'].astype(str) == id_val]
                
                if len(predelib_matches) == 0:
                    logger.warning(f"No predelib records found for ID: {id_val}")
                    continue
                    
                if len(dashboard_matches) == 0:
                    logger.warning(f"No dashboard records found for ID: {id_val}")
                    continue
                
                predelib_sp = predelib_matches['Totaal aantal SP'].iloc[0]
                dashboard_sp = dashboard_matches['Ingeschr. SP (intern)'].iloc[0]
                name_student = predelib_matches['Voornaam'].iloc[0] + ' ' + predelib_matches['Achternaam'].iloc[0]
                
                # Handle potential NaN values
                if pd.isna(predelib_sp) or pd.isna(dashboard_sp):
                    logger.warning(f"NaN values found for ID {id_val}: Predelib={predelib_sp}, Dashboard={dashboard_sp}")
                    continue
                
                # Convert to comparable types
                try:
                    predelib_sp_num = float(predelib_sp) if not pd.isna(predelib_sp) else 0
                    dashboard_sp_num = float(dashboard_sp) if not pd.isna(dashboard_sp) else 0
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error converting SP values to numbers for ID {id_val}: {e}")
                    # Fall back to string comparison
                    predelib_sp_num = str(predelib_sp)
                    dashboard_sp_num = str(dashboard_sp)
                
                if predelib_sp_num != dashboard_sp_num:
                    mismatch = {
                        'ID': id_val,
                        'Name': name_student,
                        'Predelib_SP': predelib_sp,
                        'Dashboard_SP': dashboard_sp,
                        
                    }
                    mismatches.append(mismatch)
                    logger.debug(f"Mismatch found for ID {id_val}: Predelib={predelib_sp}, Dashboard={dashboard_sp}")
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing ID {id_val}: {e}")
                continue
        
        logger.info(f"Successfully processed {processed_count} matching records")
        
        if len(mismatches) == 0:
            logger.info("All SP values match between the two dataframes!")
        else:
            logger.warning(f"Found {len(mismatches)} mismatches")
            for mismatch in mismatches:
                logger.info(f"Mismatch - ID {mismatch['ID']} ({mismatch['Name']}): Predeliberatierapport SP={mismatch['Predelib_SP']}, Dashboard Inschrijvingen SP={mismatch['Dashboard_SP']}")
        
        return mismatches
        
    except Exception as e:
        logger.error(f"Unexpected error in compare_sp_values: {e}")
        raise


if __name__ == "__main__":
    # Example usage - can be used for testing
    logger.info("Starting SP comparison script")
    
    try:
        from checkheaders import check_headers_predelibfile, check_headers_dashboard_inschrijvingenfile
        
        # Read the Excel files
        logger.info("Reading Excel files")
        try:
            df_predelib = pd.read_excel('db.xlsx')
            logger.info(f"Successfully loaded predelib file with shape: {df_predelib.shape}")
        except FileNotFoundError:
            logger.error("db.xlsx file not found")
            raise
        except Exception as e:
            logger.error(f"Error reading db.xlsx: {e}")
            raise
            
        try:
            df_dashboard = pd.read_excel('dashboard_inschrijvingen.xlsx')
            logger.info(f"Successfully loaded dashboard file with shape: {df_dashboard.shape}")
        except FileNotFoundError:
            logger.error("dashboard_inschrijvingen.xlsx file not found")
            raise
        except Exception as e:
            logger.error(f"Error reading dashboard_inschrijvingen.xlsx: {e}")
            raise
        
        # Process the dataframes
        logger.info("Processing dataframes")
        try:
            processed_predelib_df = check_headers_predelibfile(df_predelib)
            logger.info(f"Processed predelib dataframe shape: {processed_predelib_df.shape}")
        except Exception as e:
            logger.error(f"Error processing predelib file: {e}")
            raise
            
        try:
            processed_dashboard_df = check_headers_dashboard_inschrijvingenfile(df_dashboard)
            logger.info(f"Processed dashboard dataframe shape: {processed_dashboard_df.shape}")
        except Exception as e:
            logger.error(f"Error processing dashboard file: {e}")
            raise
        
        # Compare SP values between the two processed dataframes
        logger.info("Starting SP values comparison")
        try:
            mismatches = compare_sp_values(processed_predelib_df, processed_dashboard_df)
            logger.info(f"SP comparison completed successfully. Found {len(mismatches)} mismatches.")
            
            # Print summary for console output
            print(f"\n{'='*50}")
            print("SP COMPARISON SUMMARY")
            print(f"{'='*50}")
            print(f"Predelib records processed: {len(processed_predelib_df)}")
            print(f"Dashboard records processed: {len(processed_dashboard_df)}")
            print(f"Mismatches found: {len(mismatches)}")
            
            if mismatches:
                print(f"\nDetailed mismatches:")
                for mismatch in mismatches:
                    print(f"  ID {mismatch['ID']}: Predelib={mismatch['Predelib_SP']}, Dashboard={mismatch['Dashboard_SP']}")
            else:
                print("\nAll SP values match perfectly!")
            print(f"{'='*50}")
            
        except Exception as e:
            logger.error(f"Error during SP comparison: {e}")
            raise
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print("Error: Could not import required modules. Make sure checkheaders.py is in the same directory.")
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        print(f"An error occurred: {e}")
        print("Check the log file 'sp_comparison.log' for detailed error information.")
    finally:
        logger.info("SP comparison script completed")
