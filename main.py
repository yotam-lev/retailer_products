import json
import csv
import os
from src.sorter import Sorter
from src.search_api import live_product_extraction

def run_batch(limit=10):
    progress_file = "progress.json"
    results_file = "data/extracted_products.csv"
    input_file = "data/sorted_results.csv"
    
    # Load state
    state = {"last_processed_index": 0, "processed_domains": []}
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            state = json.load(f)

    # Read all rows
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    processed_count = 0
    with open(results_file, 'a', encoding='utf-8', newline='') as f:
        fieldnames = ['store_id', 'product_name', 'price', 'quantity', 'measurement', 'url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if state["last_processed_index"] == 0:
            writer.writeheader()

        for i in range(state["last_processed_index"], len(reader)):
            if processed_count >= limit:
                state["last_processed_index"] = i
                break
            
            row = reader[i]
            
                        # NEW: Blacklist of social media and aggregator sites
            BLOCKED_DOMAINS = ["instagram.com", "facebook.com", "linktr.ee", "tiktok.com", "twitter.com", "linkedin.com"]
            
            # Filtering: Chain logic
            is_chain = str(row.get('chain?', '')).lower() in ['true', '1', 'yes']
            if is_chain:
                continue
                
            # Skip if there is no website URL
            website_url = row.get('website_url', '').strip()
            if not website_url:
                continue
                
            domain = website_url.split('//')[-1].split('/')[0].lower()
            
            # NEW: Skip if the domain is a social media site
            if any(blocked in domain for blocked in BLOCKED_DOMAINS):
                print(f"Skipping social media nested store: {domain}")
                continue
                
            if domain in state["processed_domains"]:
                continue
            
            # Perform extraction
            products = live_product_extraction(domain, row.get('store_id'))
            for p in products:  
                p['store_id'] = row.get('store_id')
                writer.writerow(p)
            
            state["processed_domains"].append(domain)
            processed_count += 1
        else:
            state["last_processed_index"] = len(reader)

    # Save state
    with open(progress_file, 'w') as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    run_batch(limit=10)
