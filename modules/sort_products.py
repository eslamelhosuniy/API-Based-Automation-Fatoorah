import pandas as pd


def run(input_file, output_file):
 
    try:
        print("Loading Excel file...")
        df = pd.read_excel(input_file)
        
        df['name'] = df['name'].fillna('').astype(str)
        
        print("Creating sort keys...")
        df['temp_norm_name'] = df['name'].str.lower().str.replace(r'\s+', '', regex=True)
        df['product_type'] = pd.to_numeric(df['product_type'], errors='coerce').fillna(999)
        
        print("Sorting...")
        df.sort_values(by=['temp_norm_name', 'product_type'], ascending=[True, True], inplace=True)
        
        df.drop(columns=['temp_norm_name'], inplace=True)
        
        print("Saving sorted file...")
        df.to_excel(output_file, index=False)
        print(f"Done! Saved {len(df)} items to {output_file}")
        
        return True
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
