"""
Script to process the bervo_for_sheet.csv file:
1. Fix malformed entries using a full IRI for their ID
2. Remove BERVO: or ECOSIMCONCEPT: prefix from:
   - The second and third columns (EcoSIM Variable Name, EcoSIM Other Names)
   - Additional columns: has_units, qualifiers, attributes, measured_ins, measurement_ofs, contexts, and Parents
3. Replace text IDs with unique numerical identifiers using the ECOSIM prefix
"""

import pandas as pd
import argparse
import re
import os


def fix_malformed_ids(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    """
    Fix IDs that use full IRIs instead of prefixed form.
    e.g., http://purl.obolibrary.org/obo/ECOSIMCONCEPT_OH_Minus -> ECOSIMCONCEPT:OH_Minus

    Args:
        df: DataFrame containing the CSV data
        id_col: The name of the ID column in the DataFrame

    Returns:
        DataFrame with fixed IDs
    """
    # Regular expression to match full IRIs for ECOSIM and ECOSIMCONCEPT
    bervo_iri_pattern = r'http://purl\.obolibrary\.org/obo/ECOSIM_(.+)'
    bervoconcept_iri_pattern = r'http://purl\.obolibrary\.org/obo/ECOSIMCONCEPT_(.+)'

    # Also get the other id columns - handle different possible naming patterns
    id_col2 = None
    id_col3 = None
    
    # Try different patterns for secondary ID columns
    if f"{id_col}.1" in df.columns:
        id_col2 = f"{id_col}.1"
    elif "oboInOwl:id.1" in df.columns:
        id_col2 = "oboInOwl:id.1"
    elif "ID.1" in df.columns:
        id_col2 = "ID.1"
        
    if f"{id_col}.2" in df.columns:
        id_col3 = f"{id_col}.2"
    elif "oboInOwl:id.2" in df.columns:
        id_col3 = "oboInOwl:id.2"
    elif "ID.2" in df.columns:
        id_col3 = "ID.2"
    
    print(f"Using ID column: {id_col}")
    if id_col2:
        print(f"Using secondary ID column: {id_col2}")
    if id_col3:
        print(f"Using tertiary ID column: {id_col3}")
    
    # Make sure the main ID column exists
    if id_col not in df.columns:
        raise KeyError(f"Column '{id_col}' not found in the CSV file. Available columns: {df.columns.tolist()}")

    # Fix IDs in the ID column
    df[id_col] = df[id_col].apply(
        lambda x: re.sub(bervo_iri_pattern, r'BERVO:\1', str(x))
    )
    df[id_col] = df[id_col].apply(
        lambda x: re.sub(bervoconcept_iri_pattern,
                         r'ECOSIMCONCEPT:\1', str(x))
    )

    # Also fix in the other ID columns
    if id_col2 in df.columns:
        df[id_col2] = df[id_col2].apply(
            lambda x: re.sub(bervo_iri_pattern, r'BERVO:\1', str(x))
        )
        df[id_col2] = df[id_col2].apply(
            lambda x: re.sub(bervoconcept_iri_pattern,
                            r'ECOSIMCONCEPT:\1', str(x))
        )

    if id_col3 in df.columns:
        df[id_col3] = df[id_col3].apply(
            lambda x: re.sub(bervo_iri_pattern, r'BERVO:\1', str(x))
        )
        df[id_col3] = df[id_col3].apply(
            lambda x: re.sub(bervoconcept_iri_pattern,
                            r'ECOSIMCONCEPT:\1', str(x))
        )

    return df


def remove_prefixes_from_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove BERVO: and ECOSIMCONCEPT: prefixes from the specified columns:
    - oboInOwl:id.1 and oboInOwl:id.2 (EcoSIM Variable Name, EcoSIM Other Names)
    - Additional columns: has_units, qualifiers, attributes, measured_ins, measurement_ofs, contexts, and Parents

    Args:
        df: DataFrame containing the CSV data

    Returns:
        DataFrame with prefixes removed from specified columns
    """
    # Get the relevant column names from the new format
    id_col2 = 'oboInOwl:id.1'
    id_col3 = 'oboInOwl:id.2'

    # Additional columns to process
    additional_columns = [
        'has_units',        
        'qualifiers',       
        'attributes',       
        'measured_ins',     
        'measurement_ofs',  
        'contexts',         
        'parents'           
    ]

    print(f"Processing ID column 2: {id_col2}")
    print(f"Processing ID column 3: {id_col3}")
    
    if id_col2 in df.columns:
        print(f"Sample values from {id_col2} before: {df[id_col2].iloc[2:7].tolist()}")

        # Remove prefixes from second column
        df[id_col2] = df[id_col2].apply(
            lambda x: re.sub(r'^BERVO:', '', str(x))
        )
        df[id_col2] = df[id_col2].apply(
            lambda x: re.sub(r'^ECOSIMCONCEPT:', '', str(x))
        )

        print(f"Sample values from {id_col2} after: {df[id_col2].iloc[2:7].tolist()}")
    
    if id_col3 in df.columns:
        print(f"Sample values from {id_col3} before: {df[id_col3].iloc[2:7].tolist()}")

        # Remove prefixes from third column
        # This column might contain multiple values separated by |
        df[id_col3] = df[id_col3].apply(
            lambda x: '|'.join([
                re.sub(r'^BERVO:', '', term.strip()) for term in str(x).split('|')
            ])
        )
        df[id_col3] = df[id_col3].apply(
            lambda x: '|'.join([
                re.sub(r'^ECOSIMCONCEPT:', '', term.strip()) for term in str(x).split('|')
            ])
        )

        print(f"Sample values from {id_col3} after: {df[id_col3].iloc[2:7].tolist()}")

    # Process additional columns
    for col_name in additional_columns:
        if col_name in df.columns:
            print(f"Processing column: {col_name}")
            # Replace NaN values with empty strings first
            df[col_name] = df[col_name].fillna('')
            # Each column may contain multiple values separated by |
            df[col_name] = df[col_name].apply(
                lambda x: '|'.join([
                    re.sub(r'^BERVO:', '', term.strip()) for term in str(x).split('|')
                ])
            )
            df[col_name] = df[col_name].apply(
                lambda x: '|'.join([
                    re.sub(r'^ECOSIMCONCEPT:', '', term.strip()) for term in str(x).split('|')
                ])
            )
            # Replace string 'nan' with empty string
            df[col_name] = df[col_name].apply(
                lambda x: '' if str(x).lower() == 'nan' else str(x)
            )
            # Show sample of changes for first additional column
            if col_name == additional_columns[0]:
                print(f"Sample values from {col_name} after: {df[col_name].iloc[2:7].tolist()}")

    return df


def replace_ids_with_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace text IDs with unique numerical identifiers.
    All identifiers will use the ECOSIM prefix with a five-digit pattern.
    
    Special handling for:
    - Object properties: Use label with ECOSIM prefix (e.g., BERVO:has_unit)
    - Annotation properties: Use IRI from first column
    - If no label is available, use the original identifier

    Args:
        df: DataFrame containing the CSV data

    Returns:
        DataFrame with numeric IDs
    """
    # Create a mapping of old IDs to new IDs
    id_mapping = {}
    counter = 1
    
    # Get column names
    iri_col_name = 'IRI'
    id_col = 'oboInOwl:id'
    label_col = 'LABEL'
    type_col = 'Type'
    
    # Skip the header rows (first 2 rows)
    for idx, row in df.iloc[2:].iterrows():
        old_id = row[id_col]
        # Skip if already mapped
        if old_id in id_mapping:
            continue

        # Check if this is an object or annotation property
        if type_col in df.columns and row[type_col] in ['Object property', 'Annotation property']:
            # For annotation properties, use the IRI from the first column
            # because these are generally imported
            if row[type_col] == 'Annotation property':
                # Extract the local name from the IRI
                iri = str(row[iri_col_name]).strip()
                new_id = iri
            # For object properties, check if Label is available
            elif row[type_col] == 'Object property' and label_col in df.columns and pd.notna(row[label_col]) and str(row[label_col]).strip() != '':
                # Clean the label for object properties
                cleaned_label = str(row[label_col]).strip().lower()
                cleaned_label = re.sub(r'[^a-z0-9_]', '_', cleaned_label)
                new_id = f"BERVO:{cleaned_label}"
            # If no appropriate value found but we have a non-empty ID, keep the original ID
            elif pd.notna(old_id) and str(old_id).strip() != '' and str(old_id).lower() != 'nan':
                new_id = str(old_id)
            else:
                # Last resort - generate a numeric ID
                new_id = f"BERVO:{counter:05d}"
                counter += 1
        else:
            # For regular classes, create new numeric ID with ECOSIM prefix
            new_id = f"BERVO:{counter:05d}"
            counter += 1

        id_mapping[old_id] = new_id

    # Apply the mapping to the ID column
    # For the first two rows (headers), keep the original values
    header_rows = df.iloc[:2].copy()
    data_rows = df.iloc[2:].copy()

    # Convert mapping to string keys
    string_id_mapping = {str(k): v for k, v in id_mapping.items()}

    # Apply mapping with fallback
    data_rows[id_col] = data_rows[id_col].apply(
        lambda x: string_id_mapping.get(str(x), str(x))
    )

    # Combine header and data rows
    result_df = pd.concat([header_rows, data_rows], ignore_index=True)

    return result_df


def process_csv_file(input_file: str, output_file: str) -> None:
    """
    Process the bervo_for_sheet.csv file according to requirements.

    Args:
        input_file: Path to the input CSV file
        output_file: Path to the output CSV file
    """
    print(f"Reading CSV file: {input_file}")

    # Read the CSV file
    try:
        df = pd.read_csv(input_file)
        print(f"Successfully read CSV with {len(df)} rows")
        print(f"Columns in CSV: {df.columns.tolist()}")
        
        # Store the name of the first column (IRI column) to remove it later
        iri_column = df.columns[0] if len(df.columns) > 0 else 'IRI'
        print(f"First column (assumed to be IRI column): {iri_column}")
        
        # Identify the ID column - look for 'oboInOwl:id' or 'ID'
        id_col = None
        if 'oboInOwl:id' in df.columns:
            id_col = 'oboInOwl:id'
            print(f"Found ID column: {id_col}")
        elif 'ID' in df.columns:
            id_col = 'ID'
            print(f"Found ID column: {id_col}")
        else:
            # Look for columns that might be ID columns
            id_like_columns = [col for col in df.columns if 'id' in col.lower()]
            if id_like_columns:
                id_col = id_like_columns[0]
                print(f"No standard ID column found. Using {id_col} as the ID column")
            else:
                print(f"WARNING: No ID column found in the CSV file. Available columns: {df.columns.tolist()}")
                # Use the second column as a fallback (after the IRI column)
                if len(df.columns) > 1:
                    id_col = df.columns[1]
                    print(f"Using {id_col} as a fallback ID column")
                else:
                    raise ValueError("Cannot identify an ID column in the CSV file")
        
        # Debugging: Check for Type values
        if 'Type' in df.columns:
            type_values = df['Type'].unique()
            print(f"Unique Type values: {type_values}")
            
            # Count object and annotation properties
            obj_props = df[df['Type'] == 'Object property'].shape[0]
            ann_props = df[df['Type'] == 'Annotation property'].shape[0]
            print(f"Found {obj_props} object properties and {ann_props} annotation properties")
        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Apply the processing steps
    print("Fixing malformed IDs...")
    df = fix_malformed_ids(df, id_col)

    print("Removing prefixes from columns...")
    df = remove_prefixes_from_columns(df)

    print("Replacing text IDs with numeric IDs...")
    df = replace_ids_with_numeric(df)

    # Convert NaN values to empty strings
    print("Converting NaN values to empty strings...")
    df = df.fillna('')

    # Replace string 'nan' values with empty strings
    print("Replacing string 'nan' values with empty strings...")
    for col in df.columns:
        df[col] = df[col].apply(lambda x: '' if str(
            x).lower() == 'nan' else str(x))
    
    # Remove the IRI column (first column)
    print(f"Removing IRI column: {iri_column}")
    if iri_column in df.columns:
        df = df.drop(columns=[iri_column])
    
    # Rename the ID column back to 'ID' to maintain compatibility
    if id_col in df.columns:
        df = df.rename(columns={id_col: 'ID'})
        print(f"Renamed {id_col} to ID")
    elif 'ID' not in df.columns:
        # If neither oboInOwl:id nor ID exists, we have a problem
        print(f"WARNING: Neither '{id_col}' nor 'ID' column found in the data. Available columns: {df.columns.tolist()}")
        # Check if we have any columns with 'id' in their name (case insensitive)
        id_like_columns = [col for col in df.columns if 'id' in col.lower()]
        if id_like_columns:
            print(f"Found possible ID columns: {id_like_columns}")
            # Use the first one as a fallback
            df = df.rename(columns={id_like_columns[0]: 'ID'})
            print(f"Renamed {id_like_columns[0]} to ID as a fallback")

    # Write the processed data to the output file
    try:
        print(f"Writing processed CSV to: {output_file}")
        # Use na_rep='' to ensure NaN values are represented as empty strings in the CSV
        df.to_csv(output_file, index=False, na_rep='')
        print(f"Processed CSV saved to {output_file}")
    except Exception as e:
        print(f"Error writing to output file: {e}")
        raise


def main() -> None:
    """
    Main function to handle command-line arguments and execute the processing.
    """
    parser = argparse.ArgumentParser(
        description='Process the bervo_for_sheet.csv file to fix IDs and apply transformations.'
    )
    parser.add_argument('--input', default='../ontology/bervo_for_sheet.csv',
                        help='Path to the input CSV file (default: ../ontology/bervo_for_sheet.csv)')
    parser.add_argument('--output', default='../ontology/bervo_for_sheet_processed.csv',
                        help='Path for the output processed CSV file (default: ../ontology/bervo_for_sheet_processed.csv)')
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
