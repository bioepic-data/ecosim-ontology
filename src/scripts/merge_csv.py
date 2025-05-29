# A small script to merge multiple CSV files into one

import pandas as pd
import argparse
import os


def get_first_column_name(file_path):
    """
    Get the name of the first column in a CSV file.

    Args:
        file_path (str): Path to the CSV file

    Returns:
        str: Name of the first column
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        df = pd.read_csv(file_path, nrows=0)
        if len(df.columns) == 0:
            raise ValueError(f"No columns found in {file_path}")
        return df.columns[0]
    except pd.errors.EmptyDataError:
        raise ValueError(f"Empty CSV file: {file_path}")


def merge_csv_files(primary_file, secondary_file, output_file, join_type='left', remove_first_column=False):
    """
    Merge two CSV files based on their first columns and save the result.

    Args:
        primary_file (str): Path to the primary CSV file
        secondary_file (str): Path to the secondary CSV file
        output_file (str): Path for the output merged CSV file
        join_type (str): Type of join to perform (default: 'left')
        remove_first_column (bool): Whether to remove the first column from the output file (default: False)
    """
    # Get the names of the first columns
    primary_first_col = get_first_column_name(primary_file)
    secondary_first_col = get_first_column_name(secondary_file)

    # Read the CSV files
    primary_df = pd.read_csv(primary_file)
    secondary_df = pd.read_csv(secondary_file)

    # Rename the first column of secondary_df to match primary_df for merging
    secondary_df = secondary_df.rename(
        columns={secondary_first_col: primary_first_col})

    # Merge the dataframes on the first column
    merged_df = pd.merge(
        primary_df,
        secondary_df,
        on=primary_first_col,
        how=join_type
    )
    
    # Remove the first column if specified
    if remove_first_column:
        merged_df = merged_df.drop(columns=[primary_first_col])
        
    # Write the merged data to a new CSV file
    merged_df.to_csv(output_file, index=False)


def main():
    """
    Main function to handle command-line arguments and execute the merge operation.
    """
    parser = argparse.ArgumentParser(
        description='Merge two CSV files based on a common column.')
    parser.add_argument('primary_file', help='Path to the primary CSV file')
    parser.add_argument(
        'secondary_file', help='Path to the secondary CSV file')
    parser.add_argument(
        'output_file', help='Path for the output merged CSV file')
    parser.add_argument('--join-type', default='left',
                        help='Type of join to perform (default: left)')
    parser.add_argument('--remove-first-column', action='store_true',
                        help='Remove the first column from the output file')

    args = parser.parse_args()

    merge_csv_files(args.primary_file, args.secondary_file, args.output_file,
                    args.join_type, args.remove_first_column)


if __name__ == "__main__":
    main()
