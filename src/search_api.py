from src.serper_search import get_product_urls
from src.scraper import scrape_and_parse

def live_product_extraction(domain, store_id):
    print(f"Starting Live Extraction for {domain}")
    urls = get_product_urls(domain)
    results = []
    
    # Non-product keywords for URL validation
    ignored_keywords = [
        "/about", "about-us", "/contact", "contact-us", "/shipping", 
        "/delivery", "/returns", "/refund", "/terms", "/privacy", 
        "/cart", "/checkout", "/account", "/login", "/register", 
        "/blog", "/news", "/faq", "/help", "/support"
    ]
    
    for url in urls:
        url_lower = url.lower()
        if any(keyword in url_lower for keyword in ignored_keywords):
            print(f"Skipping non-product URL: {url}")
            continue
            
        print(f"\n>> PROCESSING URL: {url}")
        data = scrape_and_parse(url)
        if data and "error" not in data:
            data["url"] = url
            results.append(data)
            
    return results