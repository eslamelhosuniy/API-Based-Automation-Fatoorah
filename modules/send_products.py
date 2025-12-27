import pandas as pd
import requests
import json
import time


def run(products_file, units_mapping, categories_mapping, cache_file, token, api_base, headers,tax_id,stock_id):
   
    try:
        print("Loading data...")
        df = pd.read_excel(products_file)
            
        with open(units_mapping, 'r', encoding='utf-8') as f:
            units_map = json.load(f)
        
        with open(categories_mapping, 'r', encoding='utf-8') as f:
            cats_map = json.load(f)
            
    except Exception as e:
        print(f"Error loading files: {e}")
        return False

    units_map = {k.strip(): v for k, v in units_map.items()}
    cats_map = {k.strip(): v for k, v in cats_map.items()}
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
            type1_cache = checkpoint.get("type1_ids", {})
            processed_indices = set(checkpoint.get("processed_indices", []))
            print(f"Resuming... {len(processed_indices)} items already processed.")
    except FileNotFoundError:
        type1_cache = {}
        processed_indices = set()
        print("Starting fresh upload...")

    used_barcodes = set()
    success_count = 0
    fail_count = 0
    
    print(f"Processing {len(df)} products...")
    
    for index, row in df.iterrows():
        if index in processed_indices:
            continue
            
        try:
            name = str(row['name']).strip()
            p_type = int(row['product_type'])
            
            unit_name = str(row['unit']).strip()
            cat_name = str(row['category']).strip()
            
            unit_id = units_map.get(unit_name, 14656) 
            cat_id = cats_map.get(cat_name, 4470)
            
            barcode = str(row['bar_code']).strip() if pd.notna(row['bar_code']) else ""
            
            req_headers = headers.copy()
            if 'Content-Type' in req_headers:
                del req_headers['Content-Type']
            
            payload = {
                "name": name,
                "buyPrice": str(row['buy_price']) if pd.notna(row['buy_price']) else "0",
                "salePrice": str(row['sale_price']),
                "defaultParCode": barcode,
                "type": "1",
                "unit_id": str(unit_id),
                "stock_id": str(stock_id),
                "first_quantity": str(row['first_quantity']) if pd.notna(row['first_quantity']) else "0",
                "main_cat_id": str(cat_id),
                "product_type": str(p_type),
                "is_active": "1",
                "is_unique": "0",
                "standard_barcode_type": "gs1",
                "tag_id": "1",
                "status": "1",
                "is_online": "1",
                "salePriceWithTax": str(float(row['sale_price']) * 1.15),
                "price_including_tax": "0",
                "unifiedBarcodeType": "1212",
                "tax[0][type]": "main",
                "tax[0][id]": str(tax_id)
            }
            
            if p_type == 1:
                print(f"[{index}] Sending Type 1: {name}")
                resp = requests.post(f"{api_base}/create", headers=req_headers, data=payload)
                
                if resp.status_code == 200 and resp.json().get('status') == 0:
                    msg = resp.json().get('message', '')
                    if "default par code" in msg or "taken" in msg or "بالفعل" in msg:
                        print(f"  -> Duplicate Barcode")
                        fail_count += 1
                        continue

                if resp.status_code == 200 and resp.json().get('status') == 1:
                    new_id = resp.json()['data']['id']
                    type1_cache[name] = new_id
                    print(f"  -> Success! ID: {new_id}")
                    success_count += 1
                    
                    processed_indices.add(index)
                    with open(cache_file, 'w', encoding='utf-8') as f:
                         json.dump({"type1_ids": type1_cache, "processed_indices": list(processed_indices)}, f)
                else:
                    print(f"  -> Failed: {resp.text[:200]}")
                    fail_count += 1
                    
            elif p_type == 5:
                print(f"[{index}] Sending Type 5: {name}")
                base_id = type1_cache.get(name)
                
                if not base_id:
                    print(f"  -> Error: Base product (Type 1) not found in cache.")
                    fail_count += 1
                    continue
                    
                conv_rate = row['Conversion_rate'] if pd.notna(row['Conversion_rate']) else 1
                
                payload["complex_products[0][quantity]"] = str(conv_rate)
                payload["complex_products[0][unique_id]"] = str(base_id)
                payload["complex_products[0][discount]"] = "0"
                
                resp = requests.post(f"{api_base}/create", headers=req_headers, data=payload)

                if resp.status_code == 200 and resp.json().get('status') == 0:
                    msg = resp.json().get('message', '')
                    if "default par code" in msg or "taken" in msg or "بالفعل" in msg:
                        print(f"  -> Duplicate Barcode")
                        fail_count += 1
                        continue
                
                if resp.status_code == 200 and resp.json().get('status') == 1:
                    new_id = resp.json()['data']['id']
                    print(f"  -> Success! ID: {new_id} (Linked to {base_id})")
                    success_count += 1
                    
                    processed_indices.add(index)
                    with open(cache_file, 'w', encoding='utf-8') as f:
                         json.dump({"type1_ids": type1_cache, "processed_indices": list(processed_indices)}, f)
                else:
                    print(f"  -> Failed: {resp.text[:200]}")
                    fail_count += 1
            
            time.sleep(0.1)
            
        except Exception as e:
            print(f"[{index}] Exception: {e}")
            fail_count += 1
            
    print(f"\n{'='*50}")
    print(f"Processing Complete ....")
    print(f"Success: {success_count}")
    print(f"Failed: {fail_count}")
    print(f"{'='*50}")
    
    return True
