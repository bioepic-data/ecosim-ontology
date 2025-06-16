#!/usr/bin/env python3
# filepath: /home/harry/ecosim-ontology/src/scripts/process_ecosim_csv.py
"""
Script to process the ecosim_for_sheet.csv file:
1. Fix malformed entries using a full IRI for their ID
2. Remove ECOSIM: or ECOSIMCONCEPT: prefix from the second and third columns
3. Replace text IDs with unique numerical identifiers using the ECOSIM prefix
"""

import pandas as pd
import argparse
import re
import os
from typing import Dict, List, Tuple


def fix_malformed_ids(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fix IDs that use full IRIs instead of prefixed form.
    e.g., http://purl.obolibrary.org/obo/ECOSIMCONCEPT_OH_Minus -> ECOSIMCONCEPT:OH_Minus
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        DataFrame with fixed IDs
    """
    # Regular expression to match full IRIs for ECOSIM and ECOSIMCONCEPT
    ecosim_iri_pattern = r'http://purl\.obolibrary\.org/obo/ECOSIM_(.+)'
    ecosimconcept_iri_pattern = r'http://purl\.obolibrary\.org/obo/ECOSIMCONCEPT_(.+)'
    
    # Fix IDs in the first column
    df['ID'] = df['ID'].apply(
        lambda x: re.sub(ecosim_iri_pattern, r'ECOSIM:\1', str(x))
    )
    df['ID'] = df['ID'].apply(
        lambda x: re.sub(ecosimconcept_iri_pattern, r'ECOSIMCONCEPT:\1', str(x))
    )
    
    # Also fix in the second and third columns (which will have prefixes removed later)
    col2_name = df.columns[1]
    col3_name = df.columns[2]
    
    df[col2_name] = df[col2_name].apply(
        lambda x: re.sub(ecosim_iri_pattern, r'ECOSIM:\1', str(x))
    )
    df[col2_name] = df[col2_name].apply(
        lambda x: re.sub(ecosimconcept_iri_pattern, r'ECOSIMCONCEPT:\1', str(x))
    )
    
    df[col3_name] = df[col3_name].apply(
        lambda x: re.sub(ecosim_iri_pattern, r'ECOSIM:\1', str(x))
    )
    df[col3_name] = df[col3_name].apply(
        lambda x: re.sub(ecosimconcept_iri_pattern, r'ECOSIMCONCEPT:\1', str(x))
    )
    
    return df


def remove_prefixes_from_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove ECOSIM: and ECOSIMCONCEPT: prefixes from the second and third columns.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        DataFrame with prefixes removed from specified columns
    """
    col2_name = df.columns[1]
    col3_name = df.columns[2]
    
    print(f"Column 2 name: {col2_name}")
    print(f"Column 3 name: {col3_name}")
    print(f"Sample values from column 2 before: {df[col2_name].iloc[2:7].tolist()}")
    
    # Remove prefixes from second column
    df[col2_name] = df[col2_name].apply(
        lambda x: re.sub(r'^ECOSIM:', '', str(x))
    )
    df[col2_name] = df[col2_name].apply(
        lambda x: re.sub(r'^ECOSIMCONCEPT:', '', str(x))
    )
    
    print(f"Sample values from column 2 after: {df[col2_name].iloc[2:7].tolist()}")
    print(f"Sample values from column 3 before: {df[col3_name].iloc[2:7].tolist()}")
    
    # Remove prefixes from third column
    # This column might contain multiple values separated by |
    df[col3_name] = df[col3_name].apply(
        lambda x: '|'.join([
            re.sub(r'^ECOSIM:', '', term.strip()) for term in str(x).split('|')
        ])
    )
    df[col3_name] = df[col3_name].apply(
        lambda x: '|'.join([
            re.sub(r'^ECOSIMCONCEPT:', '', term.strip()) for term in str(x).split('|')
        ])
    )
    
    print(f"Sample values from column 3 after: {df[col3_name].iloc[2:7].tolist()}")
    
    return df


def replace_ids_with_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace text IDs with unique numerical identifiers.
    All identifiers will use the ECOSIM prefix with a five-digit pattern.
    
    Args:
        df: DataFrame containing the CSV data
        
    Returns:
        DataFrame with numeric IDs
    """
    # Create a mapping of old IDs to new IDs
    id_mapping = {}
    counter = 1
    
    # Skip the header rows (first 2 rows)
    for idx, row in df.iloc[2:].iterrows():
        old_id = row['ID']
        # Skip if already mapped
        if old_id in id_mapping:
            continue
        
        # Create new numeric ID with ECOSIM prefix
        new_id = f"ECOSIM:{counter:05d}"
        id_mapping[old_id] = new_id
        counter += 1
    
    # Apply the mapping to the ID column
    # For the first two rows (headers), keep the original values
    header_rows = df.iloc[:2].copy()
    data_rows = df.iloc[2:].copy()
    
    # Convert mapping to string keys
    string_id_mapping = {str(k): v for k, v in id_mapping.items()}
    
    # Apply mapping with fallback
    data_rows['ID'] = data_rows['ID'].apply(
        lambda x: string_id_mapping.get(str(x), str(x))
    )
    
    # Combine header and data rows
    result_df = pd.concat([header_rows, data_rows], ignore_index=True)
    
    return result_df


def process_csv_file(input_file: str, output_file: str) -> None:
    """
    Process the ecosim_for_sheet.csv file according to requirements.
    
    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
    """
    print(f"Reading CSV file: {input_file}")
    
    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Successfully read CSV with {len(df)} rows")
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return
    
    # Apply the processing steps
    print("Fixing malformed IDs...")
    df = fix_malformed_ids(df)
    
    print("Removing prefixes from columns...")
    df = remove_prefixes_from_columns(df)
    
    print("Replacing text IDs with numeric IDs...")
    df = replace_ids_with_numeric(df)
    
    # Write the processed data to the output file
    try:
        print(f"Writing processed CSV to: {output_file}")
        df.to_csv(output_file, index=False)
        print(f"Processed CSV saved to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        raise


def main() -> None:
    """
    Main function to handle command-line arguments and execute the processing.
    """
    parser = argparse.ArgumentParser(
        description='Process the ecosim_for_sheet.csv file to fix IDs and apply transformations.'
    )
    parser.add_argument('--input', default='/home/harry/ecosim-ontology/src/ontology/ecosim_for_sheet.csv',
                      help='Path to the input CSV file (default: /home/harry/ecosim-ontology/src/ontology/ecosim_for_sheet.csv)')
    parser.add_argument('--output', default='/home/harry/ecosim-ontology/src/ontology/ecosim_for_sheet_processed.csv',
                      help='Path for the output processed CSV file (default: /home/harry/ecosim-ontology/src/ontology/ecosim_for_sheet_processed.csv)')
    parser.add_argument('--verbose', action='store_true',
                      help='Enable verbose output')
    
    args = parser.parse_args()
    
    # Get absolute paths
    input_file = os.path.abspath(args.input)
    output_file = os.path.abspath(args.output)
    
    if args.verbose:
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
    
    # Validate input file exists
    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        if args.verbose:
            print(f"Creating output directory: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
    
    process_csv_file(input_file, output_file)


if __name__ == "__main__":
    main()
