import os
import requests
from typing import List
from dotenv import load_dotenv

# Force load the .env file
load_dotenv()

def get_product_urls(domain: str) -> List[str]:
    print(f"Searching domain: {domain}")
    
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        print(">>> ERROR: SERPER_API_KEY is missing! Check your .env file.")
        return []

    url = "https://google.serper.dev/search"
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    payload = {
        "q": f'site:{domain} "cat litter" OR "animal bedding" OR "horse bedding" OR "chicken bedding"'
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        organic_results = data.get("organic", [])
        print(f">>> SUCCESS: Serper found {len(organic_results)} URLs for {domain}.")
        
        return [item.get("link") for item in organic_results if "link" in item]
        
    except Exception as e:
        print(f">>> SERPER API ERROR: {e}")
        if 'response' in locals():
            print(f">>> Error Details: {response.text}")
        return []