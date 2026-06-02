# Project Requirements: Animal Bedding & Litter Scraper

## 1. Project Goal
Create an automated script that processes a CSV of store websites (100 per day), discovering specific animal bedding and litter products via search APIs. It utilizes a local Ollama LLM to filter out irrelevant products (like physical pet beds) to generate a consolidated inventory list.

## 2. Inputs
* A CSV file containing the following headers: 
  `store_id, name, address, suburb, chain?, website_url, phone_number, lat, lng, apportioned_pop, pop_density_per_sqkm`

## 3. Outputs
* **Data File:** A structured CSV (e.g., `inventory_results.csv`) containing: Store Name, Product Title, Product URL, Product Type.
* **State File:** A `progress.json` file tracking the integer index of the last processed store.

## 4. Search & Filtering Criteria
* **Target Categories:** Animal Bedding, Cat Litter.
* **Target Specifics:** Horse bedding, chicken bedding, cat litter (hay, straw, pine shavings, pellets, clay, silica, etc.).
* **Explicit Exclusions:** Physical/furniture beds (e.g., plush dog beds, memory foam cat beds, washable pet mats).

## 5. Technical Stack & Architecture
* **Language:** Python
* **Sorting Logic:** Before processing, the script will use the Haversine formula on the `lat` and `lng` columns to sort all stores by distance from coordinates `-33.761, 151.129`.
* **Pacing/State Management:** Script will process exactly 100 stores per execution, referencing `progress.json` to slice the sorted store list and determine where to start.
* **Phase 1: Discovery (Search API)** * Google Custom Search JSON API utilizing `site:` operators to bypass UI navigation and find direct product URLs (Free tier: 100 queries/day).
* **Phase 2: Content Extraction** * Web scraping library to extract the text/descriptions from the discovered product pages.
* **Phase 3: Semantic Filtering (Local LLM)** * Query locally hosted Qwen 3 32B model via Ollama to semantically classify the scraped text and enforce the exclusion criteria.

## 6. Open Questions / Pending Decisions
* The best web scraping library to use for the extraction phase.