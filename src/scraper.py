import os
import json
import re
import subprocess
from playwright.sync_api import sync_playwright

def scrape_and_parse(url: str):
    model = os.getenv("OLLAMA_MODEL", "qwen:14b")

    print(f"Scraping URL: {url}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(2500)
            text = page.inner_text("body")
            browser.close()
    except Exception as e:
        print(f"Playwright error: {e}")
        return None

    print(f"Playwright extracted {len(text)} characters. Preview: {text[:150]}")
    
    prompt = f"""
    You are a data extractor. Extract the animal bedding or cat litter product from the text.
    Strictly output ONLY JSON. No markdown formatting.
    Schema: {{"product_name": "name", "price": 0.00, "quantity": 0.0, "measurement": "kg", "confidence": 0-100}}
    Rules:
    - If price is missing, use 0.00.
    - If quantity is missing, use 1.0.
    - If you cannot find a specific measurement, guess based on the title or use "unit".
    - "confidence" must be an integer score between 0 and 100 indicating the confidence that this is animal bedding or cat litter.
    - If the text clearly refers to a physical furniture bed (such as a plush dog/cat bed) or human bedding, output exactly: {{"error": "invalid_item_type"}}.
    Text: {text[:4000]}
    """

    print("Sending to Ollama CLI...")
    try:
        process = subprocess.run(
            ['ollama', 'run', model],
            input=prompt,
            text=True,
            capture_output=True,
            check=True
        )
        result = process.stdout
        print(f"RAW OLLAMA OUTPUT BEFORE CLEANING:\n{result}\n-------------------")
        
        # Resilient multiline JSON block extraction matching from first '{' to last '}'
        match = re.search(r'(\{[\s\S]*\})', result)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                # Fallback to non-greedy if greedy match captured trailing text containing braces
                fallback_match = re.search(r'(\{[\s\S]*?\})', result)
                if fallback_match:
                    try:
                        return json.loads(fallback_match.group(1))
                    except json.JSONDecodeError:
                        pass
        print("No valid JSON found in output.")
        return None
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Ollama execution error: {e}")
        return None
    except Exception as e:
        print(f"General error: {e}")
        return None
