import pandas as pd

def check_headers_predelibfile(df):
    # Check if the headers are already in the column names (first row)
    if 'Achternaam' in df.columns and 'Voornaam' in df.columns:
        print("Headers found in first row - file already processed, returning unchanged")
        return df  # Return the dataframe unchanged
    else:
        # Find the row index where 'Achternaam' and 'Voornaam' appear as headers
        header_row = None
        for i, row in df.iterrows():
            if 'Achternaam' in row.values and 'Voornaam' in row.values:
                header_row = i
                break

    if header_row is not None:
        # Delete all rows before the header row
        df = df.iloc[header_row:].reset_index(drop=True)

        # Set the first row as column headers
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)

        # Define the columns to keep
        columns_to_keep = [
            'ID', 'Achternaam', 'Voornaam', 'E-mail', 'Loopbaan',
            'Drempelteller omschrijving', 'Programma status omschrijving',
            'OO Periode', 'OO Studiegidsnummer', 'OO Lange omschrijving',
            'OO Eenheden', 'OO Sessie', 'OO Credit (Y/N)', 'OO Periode credit',
            'OO Programma code', 'OO Programma korte omschr.', 'Totaal aantal SP',
            'Aantal SP vereist', 'Aantal SP zonder VZP', 'Adviesrapport code',
            'Waarschuwing', 'Lijsttype'
        ]

        # Keep only the specified columns (only if they exist in the dataframe)
        existing_columns = [col for col in columns_to_keep if col in df.columns]
        df = df[existing_columns]

        print(f"Deleted {header_row} rows, set proper headers, and kept {len(existing_columns)} columns")
    else:
        print("Headers 'Achternaam' and 'Voornaam' not found in the file")
        return df
    
    if 'Programma status omschrijving' in df.columns:
        before = len(df)
        mask = df['Programma status omschrijving'].astype(str).str.contains(r'\bBeëindigd\b', case=False, na=False)
        df = df[~mask].reset_index(drop=True)
        removed = before - len(df)
        print(f"Removed {removed} rows where Programma status omschrijving contains 'Beëindigd'")
    else:
        print("Column 'Programma status omschrijving' not found; no rows removed")

    return df
    



def check_headers_dashboard_inschrijvingenfile(df):
    # Check if the headers are already in the column names (first row)
    if 'Naam' in df.columns and 'Voornaam' in df.columns:
        print("Headers found in first row  of dashboard_inschrijvingen - no need to search for header row")
        header_row = -1  # Indicates headers are already set
    else:
        # Find the row index where 'Naam' and 'Voornaam' appear as headers
        header_row = None
        for i, row in df.iterrows():
            if 'Naam' in row.values and 'Voornaam' in row.values:
                header_row = i
                break

    # Apply headers only when a valid header row was found (>= 0)
    if header_row is not None and header_row >= 0:
        # Delete all rows before the header row
        df = df.iloc[header_row:].reset_index(drop=True)

        # Set the first row as column headers
        df.columns = df.iloc[0]
        df = df.iloc[1:].reset_index(drop=True)

        print(f"Deleted {header_row} rows in dashboard_file, set proper headers")
    elif header_row == -1:
        # Headers were already correct; nothing to change
        print("Headers were already correct in dashboard_file.")
    else:
        print("Headers 'Naam' and 'Voornaam' not found in the file")
        return df

    # Remove rows where Status contains 'Beëindigd'
    if 'Status' in df.columns:
        before = len(df)
        mask = df['Status'].astype(str).str.contains(r'\bBeëindigd\b', case=False, na=False)
        df = df[~mask].reset_index(drop=True)
        removed = before - len(df)
        print(f"Removed {removed} rows where Status contains 'Beëindigd'")
    else:
        print("Column 'Status' not found; no rows removed")

    return df


if __name__ == "__main__":
    # Read the Excel files
    df_predelib = pd.read_excel('db.xlsx')
    df_dashboard = pd.read_excel('dashboard_inschrijvingen.xlsx')
    
    # Process the dataframes
    processed_predelib_df = check_headers_predelibfile(df_predelib)
    processed_dashboard_df = check_headers_dashboard_inschrijvingenfile(df_dashboard)

