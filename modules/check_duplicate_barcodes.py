import pandas as pd
from collections import Counter


def run(input_file, output_report):

    print("Loading Excel file...")
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return False
    
    print(f"Total products: {len(df)}")
    
    if 'bar_code' not in df.columns:
        print("Error: 'bar_code' column not found")
        return False
    
    df_with_barcodes = df[df['bar_code'].notna()].copy()
    df_with_barcodes['bar_code'] = df_with_barcodes['bar_code'].astype(str).str.strip()
    
    df_with_barcodes = df_with_barcodes[df_with_barcodes['bar_code'] != '']
    df_with_barcodes = df_with_barcodes[df_with_barcodes['bar_code'] != 'nan']
    
    print(f"Products with barcodes: {len(df_with_barcodes)}")
    
    barcode_counts = Counter(df_with_barcodes['bar_code'])
    duplicate_barcodes = {barcode: count for barcode, count in barcode_counts.items() if count > 1}
    
    if not duplicate_barcodes:
        print("\n No duplicate barcodes found!")
        return True
    
    print(f"\n  Found {len(duplicate_barcodes)} duplicate barcodes")
    print(f"Total duplicate entries: {sum(duplicate_barcodes.values())}")
    
    duplicate_rows = []
    for barcode, count in sorted(duplicate_barcodes.items(), key=lambda x: x[1], reverse=True):
        rows = df_with_barcodes[df_with_barcodes['bar_code'] == barcode].copy()
        rows['duplicate_count'] = count
        duplicate_rows.append(rows)
    
    if duplicate_rows:
        result_df = pd.concat(duplicate_rows, ignore_index=True)
        
        important_cols = ['bar_code', 'duplicate_count', 'name', 'product_type', 'sale_price', 'buy_price']
        other_cols = [col for col in result_df.columns if col not in important_cols]
        result_df = result_df[important_cols + other_cols]
        
        result_df.to_excel(output_report, index=False)
        print(f"\n Report saved to: {output_report}")
        
    return True
