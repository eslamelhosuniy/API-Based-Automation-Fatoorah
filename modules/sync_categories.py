import pandas as pd
import requests
import json
import time


def run(input_file, output_mapping, token, api_base, headers):
   
    try:
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"Error loading file: {e}")
        return False

    if 'category' not in df.columns:
        print("Error: 'category' column not found")
        return False

    categories = df['category'].dropna().astype(str).unique()
    print(f"Found {len(categories)} distinct categories")
    
    mapping = {}
    
    for cat_name in categories:
        cat_name = cat_name.strip()
        if not cat_name:
            continue
            
        print(f"Processing category: {cat_name}...")
        
        try:
            search_url = f"{api_base}/all"
            params = {"page": 1, "limit": 10, "keyword": cat_name}
            resp = requests.get(search_url, headers=headers, params=params)
            resp_json = resp.json()
            
            found_id = None
            if resp.status_code == 200 and 'data' in resp_json and 'data' in resp_json['data']:
                results = resp_json['data']['data']
                for item in results:
                    if item['name'].strip() == cat_name:
                        found_id = item['id']
                        break
            
            if found_id:
                print(f"  Found ID: {found_id}")
                mapping[cat_name] = found_id
            else:
                print(f"  Not found. Creating...")
                create_url = f"{api_base}/create"
                payload = {
                    "name": cat_name,
                    "identification_number": "",
                    "description": "",
                    "status": True
                }
                
                create_resp = requests.post(create_url, headers=headers, json=payload)
                create_json = create_resp.json()
                
                if create_resp.status_code == 200 and create_json.get('status') == 1:
                    new_data = create_json.get('data')
                    if new_data and 'id' in new_data:
                        found_id = new_data['id']
                        print(f"  Created successfully. New ID: {found_id}")
                        mapping[cat_name] = found_id
                    else:
                        print(f"  Created but ID not found in response: {create_json}")
                else:
                    print(f"  Creation failed: {create_json}")
                    
        except Exception as e:
            print(f"  Error processing {cat_name}: {e}")
            
        time.sleep(0.5)

    with open(output_mapping, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)
        
    print("Mapping saved.")
    return True
