import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fake_useragent import UserAgent
import random

# Global configuration
HEADERS = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.google.com/',
    'DNT': '1'
}
MAX_RETRIES = 3
REQUEST_DELAY = (1, 3)  # Random delay range in seconds

# Configure browser (singleton pattern)
_driver = None

def get_driver():
    global _driver
    if _driver is None:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={UserAgent().random}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            _driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        except Exception as e:
            print(f"Driver setup error: {str(e)}")
    return _driver

def close_driver():
    global _driver
    if _driver:
        _driver.quit()
        _driver = None

def make_request(url):
    headers = {**HEADERS, 'User-Agent': UserAgent().random}
    
    for attempt in range(MAX_RETRIES):
        try:
            time.sleep(random.uniform(*REQUEST_DELAY))
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

# Priority sites (CarMax first)
def search_carmax(make, model=None):
    try:
        url = f"https://www.carmax.com/cars/{make}"
        if model:
            url += f"/{model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try multiple selectors for robustness
        link_element = (soup.find('a', class_='car-tile') or 
                       soup.find('a', href=lambda href: href and f"/{make}" in href.lower()) or
                       soup.find('a', {'data-test': 'vehicleCardLink'}))
        
        if not link_element:
            return None
            
        return {
            'source': 'CarMax',
            'link': "https://www.carmax.com" + link_element['href'],
            'priority': 1  # Highest priority
        }
    except Exception as e:
        print(f"CarMax warning: {str(e)}")
        return None

# Secondary sites (simplified)
def search_autotrader(make, model=None):
    try:
        driver = get_driver()
        url = f"https://www.autotrader.com/cars-for-sale/all/{make}"
        if model:
            url += f"/{model}"
            
        driver.get(url)
        time.sleep(random.uniform(2, 4))
        
        link_element = driver.find_element("css selector", "a[href*='/cars-for-sale/vehicle']")
        return {
            'source': 'AutoTrader',
            'link': link_element.get_attribute('href'),
            'priority': 2
        }
    except Exception as e:
        print(f"AutoTrader warning: {str(e)}")
        return None
    finally:
        close_driver()

# Simplified search template for other sites
def generic_search(make, model=None, base_url=None, source=None, priority=3, 
                   link_selector=None, link_processor=None):
    try:
        url = base_url.format(make=make, model=model or '')
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = link_selector(soup)
        if not link_element:
            return None
            
        link = link_processor(link_element) if link_processor else link_element['href']
        return {
            'source': source,
            'link': link,
            'priority': priority
        }
    except Exception as e:
        print(f"{source} warning: {str(e)}")
        return None

# Configured search functions
SEARCH_FUNCTIONS = [
    # Priority 1 - CarMax (special handling)
    lambda m, md: search_carmax(m, md),
    
    # Priority 2 - AutoTrader (requires Selenium)
    lambda m, md: search_autotrader(m, md),
    
    # Priority 3 - Other sites (generic)
    lambda m, md: generic_search(
        m, md,
        base_url=f"https://www.cars.com/shopping/{{make}}/{{model}}",
        source="Cars.com",
        link_selector=lambda s: s.select_one('.vehicle-card-link'),
        link_processor=lambda e: "https://www.cars.com" + e['href']
    ),
    
    # Add other sites similarly...
]

def find_car(make="toyota", model=None):
    print(f"🔍 Searching for {make.upper()}{f' {model.upper()}' if model else ''}")
    
    results = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(func, make, model) for func in SEARCH_FUNCTIONS]
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
                # Early exit if we have a high priority result
                if result['priority'] == 1 and result['link']:
                    print("✅ Found CarMax result - prioritizing")
                    executor.shutdown(wait=False)
                    return result['link']
    
    if not results:
        print("❌ No listings found")
        return None
    
    # Sort by priority then source
    results.sort(key=lambda x: (x['priority'], x['source']))
    
    print("\nFound listings:")
    for result in results:
        print(f"{result['source']}: {result['link']}")
    
    return results[0]['link']

if __name__ == "__main__":
    try:
        car_link = find_car(make="bmw")
        if car_link:
            print(f"\n🚗 Best listing: {car_link}")
    finally:
        close_driver()