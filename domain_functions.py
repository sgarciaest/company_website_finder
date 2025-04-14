import re
import tldextract
from urllib.parse import urlparse
import csv
import requests
from bs4 import BeautifulSoup

# Function to scrape search results from bing, using requests and BeautifulSoup
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8",
#     "Accept-Language": "en-US,en;q=0.5",
#     "Accept-Encoding": "gzip, deflate, br",
#     "DNT": "1",
#     "Connection": "keep-alive",
#     "Upgrade-Insecure-Requests": "1",
#     "Sec-Fetch-Dest": "document",
#     "Sec-Fetch-Mode": "navigate",
#     "Sec-Fetch-Site": "none",
#     "Sec-Fetch-User": "?1",
#     "Cache-Control": "max-age=0"
# }

def bing_search(query):

    search_url = f"https://www.bing.com/search?q={query}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    results = []
    
    for result in soup.select(".b_algo")[:10]:
        link_tag = result.select_one("a")
        
        if link_tag and "href" in link_tag.attrs:
            link = link_tag["href"]
            
            results.append(link)
    
    return results

# Function to ensure a url starts with the specified URL scheme (hhtp or https)
# If no scheme exists, the function prepends https://
def ensure_scheme(url):
    if not url.startswith(('http://', 'https://')):
        return 'https://' + url
    return url

# Extracts the main domain (e.g., "example.com") from a given URL, ensuring a valid scheme, validating the domain with tldextract, and falling back to regex if necessary.
def get_main_page(url):
    try:
        # Ensure url scheme is http or https
        url = ensure_scheme(url)

        # Break the url into components
        parsed_url = urlparse(url)
        # Validate that the URL has a valid netloc (e.g. example.com)
        if not parsed_url.netloc:
            return None
        
        # Use tldextract (that can handle complex domains) and extract the domain and the TLD (e.g. ".com" or ".de") 
        extracted = tldextract.extract(url)
        if extracted.domain and extracted.suffix:
            return f"{extracted.domain}.{extracted.suffix}"
        
        # Only attempt regex if tldextract fails
        if not (extracted.domain and extracted.suffix):
            match = re.match(r'(?:https?://)?(?:www\.)?([a-z0-9\-]+(?:\.[a-z0-9\-]+)*\.[a-z]{2,})', parsed_url.netloc)
            if match:
                return match.group(1)
        
        return None

    except Exception as e:
        print(f"Error processing the URL '{url}': {e}")
        return None

def remove_separation_symbols(name):
    # Remove separation symbols
    name = re.sub(r'[&\'\+\-,\.]', "", name)
    return name

# Checks if the company name is contained in the domain of the URL.
def check_domain_for_company(name, url):

    # Normalize the company name
    # normalized_name = normalize_company_name(company_name) (not necessary?)
    
    # Get the main domain using get_main_page
    domain = get_main_page(url)

    # If the domain extraction was correct, it proceeds with the checking
    if domain:

        # Use tldextract to remove the TLD (that is the domain suffix remove the .com, .de, .org, etc)
        extracted = tldextract.extract(domain)
        domain_without_suffix = extracted.domain
        domain_without_suffix_and_separation_symbols = remove_separation_symbols(domain_without_suffix)
        
        # Check if the normalized company name is in the domain
        return any(word in domain_without_suffix_and_separation_symbols for word in name.split())
        # for word in normalized_name.split():
        #     if word in normalized_domain:
        #         return True

    return False