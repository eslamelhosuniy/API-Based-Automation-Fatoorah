import pandas as pd
import requests
import json
import time
import os


def run(input_file, output_mapping, token, api_base, headers):
    
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return False

    if 'unit' not in df.columns:
        print("Error: 'unit' column not found")
        return False

    mapping = {}
    if os.path.exists(output_mapping):
        try:
            with open(output_mapping, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            print(f"Loaded existing mapping with {len(mapping)} units")
        except:
            mapping = {}

    units = df['unit'].dropna().astype(str).unique()
    print(f"Found {len(units)} distinct units in file")
    
    new_count = 0
    skip_count = 0
    
    for unit_name in units:
        unit_name = unit_name.strip()
        if not unit_name:
            continue
        
        if unit_name in mapping:
            print(f"  {unit_name}: Already mapped (ID: {mapping[unit_name]})")
            skip_count += 1
            continue
            
        print(f"Processing unit: {unit_name}...")
        
        try:
            search_url = f"{api_base}/all"
            params = {"page": 1, "limit": 10, "keyword": unit_name}
            resp = requests.get(search_url, headers=headers, params=params)
            resp_json = resp.json()
            
            found_id = None
            if resp.status_code == 200 and 'data' in resp_json:
                results = resp_json['data']
                if isinstance(results, dict) and 'data' in results:
                    results = results['data']
                if isinstance(results, list):
                    for item in results:
                        if item.get('name', '').strip() == unit_name:
                            found_id = item['id']
                            break
            
            if found_id:
                print(f"  Found ID: {found_id}")
                mapping[unit_name] = found_id
                new_count += 1
            else:
                print(f"  Not found. Creating...")
                create_url = f"{api_base}/create"
                payload = {
                    "identification_number": "",
                    "short_code": unit_name[:5],
                    "name": unit_name,
                    "change_rate": 0,
                    "description": "",
                    "unit_type": "main",
                    "status": True
                }
                
                create_resp = requests.post(create_url, headers=headers, json=payload)
                create_json = create_resp.json()
                
                if create_resp.status_code == 200 and create_json.get('status') == 1:
                    new_data = create_json.get('data')
                    if new_data and 'id' in new_data:
                        found_id = new_data['id']
                        print(f"  Created successfully. New ID: {found_id}")
                        mapping[unit_name] = found_id
                        new_count += 1
                    else:
                        print(f"  Created but ID not found in response: {create_json}")
                else:
                    print(f"  Creation failed: {create_json}")
                    
        except Exception as e:
            print(f"  Error processing {unit_name}: {e}")
            
        time.sleep(0.5)

    with open(output_mapping, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)
        
    print(f"Mapping saved. New: {new_count}, Skipped: {skip_count}, Total: {len(mapping)}")
    return True
