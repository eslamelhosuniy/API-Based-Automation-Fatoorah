import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules import (
    sort_products,
    sync_units,
    sync_categories,
    check_duplicate_barcodes,
    send_products
)


def get_user_input():

    token = input("\n Enter API Token: ").strip()
    if not token:
        print(" Token is required")
        sys.exit(1)
    stock_id = input("\n Enter stock_id: ").strip()
    if not token:
        print(" stock_id is required")
        sys.exit(1)
    tax_id = input("\n Enter tax_id: ").strip()
    if not token:
        print(" tax_id is required")
        sys.exit(1)
    
    default_path = str(Path(__file__).parent)
    path_input = input(f"\n Enter base path (default: {default_path}): ").strip()
    base_path = Path(path_input) if path_input else Path(default_path)
    
    if not base_path.exists():
        print(f" Path does not exist: {base_path}")
        sys.exit(1)
    
    print(f"\n Excel files in {base_path}:")
    excel_files = list(base_path.glob("*.xlsx"))
    for i, f in enumerate(excel_files, 1):
        print(f"  {i}. {f.name}")
    
    file_choice = input("\n Enter file number or filename: ").strip()
    
    if file_choice.isdigit():
        idx = int(file_choice) - 1
        if 0 <= idx < len(excel_files):
            input_file = excel_files[idx]
        else:
            print(" Invalid choice!")
            sys.exit(1)
    else:
        input_file = base_path / file_choice
        if not input_file.exists():
            print(f" File not found: {input_file}")
            sys.exit(1)
    
    return {
        'token': token,
        'tax_id': tax_id,
        'stock_id': stock_id,
        'token': token,
        'base_path': base_path,
        'input_file': str(input_file),
        'sorted_file': str(base_path / '_sorted_products.xlsx'),
        'units_mapping': str(base_path / 'units_mapping.json'),
        'categories_mapping': str(base_path / 'categories_mapping.json'),
        'upload_cache': str(base_path / 'upload_cache.json'),
        'duplicate_report': str(base_path / 'duplicate_barcodes_report.xlsx'),
    }


def build_headers(token, include_content_type=True):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        "Origin": "https://dev.fatoorah.sa",
        "Referer": "https://dev.fatoorah.sa/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    if include_content_type:
        headers["Content-Type"] = "application/json"
    return headers


API_ENDPOINTS = {
    'product': 'https://dev-api.fatoorah.sa/apiAdmin/Product',
    'category': 'https://dev-api.fatoorah.sa/apiAdmin/Category',
    'major_unit': 'https://dev-api.fatoorah.sa/apiAdmin/MajorUnit',
}


def run_pipeline(config):
  
    
    # Step 1: Sort Products
    print("\n Step 1: Sorting Products...")
    print("-" * 40)
    sort_products.run(
        input_file=config['input_file'],
        output_file=config['sorted_file']
    )
    
    # Step 2: Sync Units
    print("\n Step 2: Syncing Units...")
    print("-" * 40)
    sync_units.run(
        input_file=config['sorted_file'],
        output_mapping=config['units_mapping'],
        token=config['token'],
        api_base=API_ENDPOINTS['major_unit'],
        headers=build_headers(config['token'])
    )
    
    # Step 3: Sync Categories
    print("\n  Step 3: Syncing Categories...")
    print("-" * 40)
    sync_categories.run(
        input_file=config['sorted_file'],
        output_mapping=config['categories_mapping'],
        token=config['token'],
        api_base=API_ENDPOINTS['category'],
        headers=build_headers(config['token'])
    )
    
    # Step 4: Check Duplicates
    print("\n Step 4: Checking Duplicate Barcodes...")
    print("-" * 40)
    check_duplicate_barcodes.run(
        input_file=config['input_file'],
        output_report=config['duplicate_report']
    )
    
    # Step 5: Send Products
    print("\n Step 5: Sending Products to API...")
    print("-" * 40)
    send_products.run(
        products_file=config['sorted_file'],
        units_mapping=config['units_mapping'],
        categories_mapping=config['categories_mapping'],
        cache_file=config['upload_cache'],
        tax_id=config['tax_id'],
        stock_id=config['stock_id'],
        token=config['token'],
        api_base=API_ENDPOINTS['product'],
        headers=build_headers(config['token'], include_content_type=False)
    )
    
    print("\n" + "=" * 60)
    print(" Pipeline Complete!")


def main():
    config = get_user_input()
    
    print("\n Configuration:")
    print(f"  - Input File: {config['input_file']}")
    print(f"  - Base Path: {config['base_path']}")
    print(f"  - Token: {config['token'][:20]}...")
    run_pipeline(config)


if __name__ == "__main__":
    main()
