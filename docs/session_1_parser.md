# Objective
Develop a robust "Serper Parser & Item Deducer" pipeline by extending `src/search_api.py` and `src/scraper.py`. The goal is to accurately parse organic search results, fetch the pages, and deduce valid inventory items using the local Ollama instance.

# Constraints
- MAX TOKEN USAGE: 1500 tokens. Be highly concise. Write only the necessary Python code. Do not output explanatory fluff.
- Model: Assume `qwen:14b` via local Ollama CLI as defined in the current environment.

# Tasks
1. **Enhance Search API (`src/search_api.py`)**: 
   - Update `live_product_extraction` to include a validation layer. After fetching URLs from `get_product_urls`, filter out obvious non-product pages (e.g., about-us, contact) using URL string matching before sending them to the scraper.
2. **Item Deduction Logic (`src/scraper.py`)**:
   - Improve the Ollama prompt inside `scrape_and_parse`. The current prompt attempts to extract "animal bedding or cat litter". 
   - Add a strict confidence score requirement to the JSON schema: `{"product_name": "name", "price": 0.00, "quantity": 0.0, "measurement": "kg", "confidence": 0-100}`.
   - If the extracted text clearly refers to a physical furniture bed or human bedding, force the deducer to output `{"error": "invalid_item_type"}`.
3. **Error Handling**:
   - Ensure the regex that matches `\{.*\}` in the Ollama stdout is resilient to multiline output and potential preamble text from the LLM. 

# Output
Provide the fully updated code for `src/search_api.py` and `src/scraper.py`.