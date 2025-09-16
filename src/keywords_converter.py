import pandas as pd
import numpy as np
import csv

def convert_keywords_format_numbered(input_file, output_file):
    """
    Convert CSV from @@ delimited keywords to multiple numbered ASSET_KEYWORDS columns
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Check if ASSET_KEYWORDS column exists
    if 'ASSET_KEYWORDS' not in df.columns:
        print("Error: 'ASSET_KEYWORDS' column not found in the CSV file")
        print(f"Available columns: {list(df.columns)}")
        return
    
    # Split keywords by @@ delimiter and create a list for each row
    keyword_lists = []
    max_keywords = 0
    
    for keywords_str in df['ASSET_KEYWORDS']:
        if pd.isna(keywords_str) or keywords_str == '':
            # Handle empty/null values
            keywords = []
        else:
            # Split by @@ and strip whitespace
            keywords = [kw.strip() for kw in str(keywords_str).split('@@') if kw.strip()]
        
        keyword_lists.append(keywords)
        max_keywords = max(max_keywords, len(keywords))
    
    # Create new dataframe with original columns (except ASSET_KEYWORDS and Unnamed columns)
    columns_to_keep = [col for col in df.columns if col != 'ASSET_KEYWORDS' and not col.startswith('Unnamed:')]
    new_df = df[columns_to_keep].copy()
    
    # Add multiple ASSET_KEYWORDS columns with proper indexing
    for i in range(max_keywords):
        # Create column names like ASSET_KEYWORDS, ASSET_KEYWORDS_2, etc.
        if i == 0:
            col_name = 'ASSET_KEYWORDS'
        else:
            col_name = f'ASSET_KEYWORDS_{i+1}'
        
        new_df[col_name] = [kw_list[i] if i < len(kw_list) else '' for kw_list in keyword_lists]
    
    # Save to CSV with custom header to have empty first column
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header with empty first column
        header = [''] + list(new_df.columns)
        writer.writerow(header)
        
        # Write data rows with first column value, replace NaN with empty string
        for index, row in new_df.iterrows():
            original_row = df.iloc[index]
            first_col_value = original_row.iloc[0] if len(original_row) > 0 else ''
            if pd.isna(first_col_value):
                first_col_value = ''
            
            # Convert row to list and replace NaN with empty string
            row_list = []
            for value in row:
                if pd.isna(value):
                    row_list.append('')
                else:
                    row_list.append(value)
            
            row_data = [first_col_value] + row_list
            writer.writerow(row_data)
    
    print(f"Conversion completed!")
    print(f"Original file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Maximum keywords found: {max_keywords}")
    print(f"Created {max_keywords} ASSET_KEYWORDS columns")
    print(f"Total rows processed: {len(df)}")

def convert_keywords_format_same_name(input_file, output_file):
    """
    Convert CSV from @@ delimited keywords to multiple ASSET_KEYWORDS columns 
    ALL with the same name using manual CSV writing
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Check if ASSET_KEYWORDS column exists
    if 'ASSET_KEYWORDS' not in df.columns:
        print("Error: 'ASSET_KEYWORDS' column not found in the CSV file")
        print(f"Available columns: {list(df.columns)}")
        return
    
    # Split keywords by @@ delimiter and create a list for each row
    keyword_lists = []
    max_keywords = 0
    
    for keywords_str in df['ASSET_KEYWORDS']:
        if pd.isna(keywords_str) or keywords_str == '':
            # Handle empty/null values
            keywords = []
        else:
            # Split by @@ and strip whitespace
            keywords = [kw.strip() for kw in str(keywords_str).split('@@') if kw.strip()]
        
        keyword_lists.append(keywords)
        max_keywords = max(max_keywords, len(keywords))
    
    # Get columns without ASSET_KEYWORDS and without Unnamed: 0
    other_columns = [col for col in df.columns if col != 'ASSET_KEYWORDS' and not col.startswith('Unnamed:')]
    
    # Create header row with empty first column, then other columns, then repeated ASSET_KEYWORDS columns
    header = [''] + other_columns + ['ASSET_KEYWORDS'] * max_keywords
    
    # Write CSV manually to allow duplicate column names
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(header)
        
        # Write data rows
        for index, row in df.iterrows():
            # Start with the first column value (from Unnamed: 0 or empty), replace NaN with empty string
            first_col_value = row.iloc[0] if len(row) > 0 else ''
            if pd.isna(first_col_value):
                first_col_value = ''
            row_data = [first_col_value]
            
            # Get values for other columns (excluding Unnamed: 0 and ASSET_KEYWORDS), replace NaN with empty string
            for col in other_columns:
                value = row[col]
                if pd.isna(value):
                    row_data.append('')
                else:
                    row_data.append(value)
            
            # Add keyword values
            keywords = keyword_lists[index]
            for i in range(max_keywords):
                if i < len(keywords):
                    row_data.append(keywords[i])
                else:
                    row_data.append('')  # Empty string for missing keywords
            
            writer.writerow(row_data)
    
    print(f"Conversion completed!")
    print(f"Original file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Maximum keywords found: {max_keywords}")
    print(f"Created {max_keywords} columns all named 'ASSET_KEYWORDS'")
    print(f"Total rows processed: {len(df)}")

def convert_keywords_format_hashtag_separate(input_file, output_file):
    """
    Convert CSV from @@ delimited keywords with hashtag separation
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output CSV file
    """
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Check if ASSET_KEYWORDS column exists
    if 'ASSET_KEYWORDS' not in df.columns:
        print("Error: 'ASSET_KEYWORDS' column not found in the CSV file")
        print(f"Available columns: {list(df.columns)}")
        return
    
    # Split keywords by @@ delimiter and separate hashtag vs regular keywords
    regular_keyword_lists = []
    hashtag_keyword_lists = []
    max_regular_keywords = 0
    
    for keywords_str in df['ASSET_KEYWORDS']:
        if pd.isna(keywords_str) or keywords_str == '':
            all_keywords = []
        else:
            all_keywords = [kw.strip() for kw in str(keywords_str).split('@@') if kw.strip()]
        
        regular_keywords = []
        hashtag_keywords = []
        
        for kw in all_keywords:
            if kw.startswith('#'):
                hashtag_keywords.append(kw)
            else:
                regular_keywords.append(kw)
        
        regular_keyword_lists.append(regular_keywords)
        hashtag_keyword_lists.append(hashtag_keywords)
        max_regular_keywords = max(max_regular_keywords, len(regular_keywords))
    
    # Get columns without ASSET_KEYWORDS and without Unnamed: 0
    other_columns = [col for col in df.columns if col != 'ASSET_KEYWORDS' and not col.startswith('Unnamed:')]
    
    # Create header with numbered regular keyword columns plus final asset_keywords column
    header = [''] + other_columns
    for i in range(max_regular_keywords):
        if i == 0:
            header.append('ASSET_KEYWORDS')
        else:
            header.append(f'ASSET_KEYWORDS_{i+1}')
    header.append('asset_keywords')  # Final column for hashtag keywords
    
    # Write CSV manually
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(header)
        
        # Write data rows
        for index, row in df.iterrows():
            # Start with the first column value, replace NaN with empty string
            first_col_value = row.iloc[0] if len(row) > 0 else ''
            if pd.isna(first_col_value):
                first_col_value = ''
            row_data = [first_col_value]
            
            # Get values for other columns, replace NaN with empty string
            for col in other_columns:
                value = row[col]
                if pd.isna(value):
                    row_data.append('')
                else:
                    row_data.append(value)
            
            # Add regular keyword values
            regular_keywords = regular_keyword_lists[index]
            for i in range(max_regular_keywords):
                if i < len(regular_keywords):
                    row_data.append(regular_keywords[i])
                else:
                    row_data.append('')  # Empty string for missing keywords
            
            # Add hashtag keywords in final column
            hashtag_keywords = hashtag_keyword_lists[index]
            hashtag_value = '@@'.join(hashtag_keywords) if hashtag_keywords else ''
            row_data.append(hashtag_value)
            
            writer.writerow(row_data)
    
    print(f"Conversion completed!")
    print(f"Original file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Maximum regular keywords found: {max_regular_keywords}")
    print(f"Created {max_regular_keywords} numbered keyword columns + 1 hashtag column")
    print(f"Total rows processed: {len(df)}")

def preview_conversion(input_file, num_rows=5):
    """
    Preview how the conversion will look for the first few rows
    
    Args:
        input_file (str): Path to input CSV file
        num_rows (int): Number of rows to preview
    """
    
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    if 'ASSET_KEYWORDS' not in df.columns:
        print("Error: 'ASSET_KEYWORDS' column not found in the CSV file")
        print(f"Available columns: {list(df.columns)}")
        return
    
    print("PREVIEW - Sample conversion:")
    print(f"Total rows in file: {len(df)}")
    print("\nBEFORE (original format with @@ delimiter):")
    
    # Show sample rows with their keywords
    sample_df = df[['RESEARCH_ASSET_ID', 'ASSET_KEYWORDS']].head(num_rows)
    for index, row in sample_df.iterrows():
        print(f"Row {index}: ID={row['RESEARCH_ASSET_ID']}")
        if pd.notna(row['ASSET_KEYWORDS']) and row['ASSET_KEYWORDS']:
            keywords = [kw.strip() for kw in str(row['ASSET_KEYWORDS']).split('@@') if kw.strip()]
            print(f"  Keywords: {keywords}")
            print(f"  Count: {len(keywords)} keywords")
        else:
            print(f"  Keywords: (empty)")
        print()
    
    # Calculate max keywords across all rows
    max_keywords = 0
    for keywords_str in df['ASSET_KEYWORDS']:
        if pd.isna(keywords_str) or keywords_str == '':
            keywords = []
        else:
            keywords = [kw.strip() for kw in str(keywords_str).split('@@') if kw.strip()]
        max_keywords = max(max_keywords, len(keywords))
    
    print(f"AFTER conversion:")
    print(f"- Maximum keywords found in any row: {max_keywords}")
    print(f"- Will create {max_keywords} separate columns")
    print(f"- Each keyword will go into its own column")
    print(f"- Empty cells for rows with fewer keywords")

# Example usage
if __name__ == "__main__":
    # Your actual file paths
    input_file = "input.csv"
    output_file_numbered = "output_numbered_columns.csv"
    output_file_same_name = "output_same_name_columns.csv"
    
    print("=== CSV Keywords Converter ===")
    print("This script converts @@ delimited keywords to multiple columns")
    print()
    
    # Show preview first
    preview_conversion(input_file, num_rows=3)
    
    print("\nThree conversion options available:")
    print("1. Numbered columns: ASSET_KEYWORDS, ASSET_KEYWORDS_2, ASSET_KEYWORDS_3, etc.")
    print("2. Same name columns: ASSET_KEYWORDS, ASSET_KEYWORDS, ASSET_KEYWORDS, etc.")
    print("3. Hashtag separation: Regular keywords in numbered columns, hashtag keywords (#psychology, etc.) in final 'asset_keywords' column")
    print()
    
    choice = input("Which option do you prefer? (1, 2, or 3): ")
    
    if choice == "1":
        print("\nConverting with numbered columns...")
        convert_keywords_format_numbered(input_file, output_file_numbered)
        print(f"\nOutput saved as: {output_file_numbered}")
    elif choice == "2":
        print("\nConverting with same name columns...")
        convert_keywords_format_same_name(input_file, output_file_same_name)
        print(f"\nOutput saved as: {output_file_same_name}")
    elif choice == "3":
        output_file_hashtag = "output_hashtag_separated.csv"
        print("\nConverting with hashtag separation...")
        convert_keywords_format_hashtag_separate(input_file, output_file_hashtag)
        print(f"\nOutput saved as: {output_file_hashtag}")
    else:
        print("Invalid choice. Please run again and select 1, 2, or 3.")
