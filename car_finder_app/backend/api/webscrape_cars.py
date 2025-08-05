# webscrape_cars.py
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
import secrets

# Configure browser with advanced settings
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(f"user-agent={UserAgent().random}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    try:
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    except Exception as e:
        print(f"Driver setup error: {str(e)}")
        return None

# Enhanced request function with retries
def make_request(url, max_retries=3):
    headers = {
        'User-Agent': UserAgent().random,
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
        'DNT': '1'
    }
    
    for attempt in range(max_retries):
        try:
            time.sleep(secrets.SystemRandom().uniform(1, 3))  # Random delay
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff

# Search functions for 13 different platforms
def search_autotrader(make, model=None):
    try:
        driver = setup_driver()
        if not driver:
            return None
            
        url = f"https://www.autotrader.com/cars-for-sale/all/{make}"
        if model:
            url += f"/{model}"
            
        driver.get(url)
        time.sleep(secrets.SystemRandom().uniform(2, 4))
        
        link_element = driver.find_element("css selector", "a[href*='/cars-for-sale/vehicle']")
        link = link_element.get_attribute('href')
        driver.quit()
        return {'source': 'AutoTrader', 'link': link}
    except Exception as e:
        print(f"AutoTrader error: {str(e)}")
        return None

def search_carmax(make, model=None):
    try:
        url = f"https://www.carmax.com/cars/{make}"
        if model:
            url += f"/{model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = (soup.find('a', class_='car-tile') or 
                      soup.find('a', href=lambda href: href and f"/{make}" in href.lower()))
        
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.carmax.com" + link_element['href']
        return {'source': 'CarMax', 'link': link}
    except Exception as e:
        print(f"CarMax error: {str(e)}")
        return None

def search_carscom(make, model=None):
    try:
        url = f"https://www.cars.com/shopping/{make}/"
        if model:
            url = f"https://www.cars.com/shopping/{make}-{model}/"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = (soup.select_one('.vehicle-card-link') or 
                      soup.find('a', href=lambda href: href and "/vehicledetail/" in href))
        
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.cars.com" + link_element['href']
        return {'source': 'Cars.com', 'link': link}
    except Exception as e:
        print(f"Cars.com error: {str(e)}")
        return None

def search_usnews(make, model=None):
    try:
        url = f"https://cars.usnews.com/cars-trucks/{make}"
        if model:
            url += f"/{model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', class_='model-link')
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://cars.usnews.com" + link_element['href']
        return {'source': 'U.S. News', 'link': link}
    except Exception as e:
        print(f"U.S. News error: {str(e)}")
        return None

def search_carvana(make, model=None):
    try:
        url = f"https://www.carvana.com/cars/{make}"
        if model:
            url += f"/{model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'data-qa': 'result-tile'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.carvana.com" + link_element['href']
        return {'source': 'Carvana', 'link': link}
    except Exception as e:
        print(f"Carvana error: {str(e)}")
        return None

def search_truecar(make, model=None):
    try:
        url = f"https://www.truecar.com/used-cars-for-sale/listings/{make}/"
        if model:
            url += f"{model}/"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'data-test': 'vehicleCardLink'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.truecar.com" + link_element['href']
        return {'source': 'TrueCar', 'link': link}
    except Exception as e:
        print(f"TrueCar error: {str(e)}")
        return None

def search_edmunds(make, model=None):
    try:
        url = f"https://www.edmunds.com/inventory/srp.html?inventorytype=used&make={make}"
        if model:
            url += f"&model={model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'class': 'usurp-inventory-card-vdp-link'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.edmunds.com" + link_element['href']
        return {'source': 'Edmunds', 'link': link}
    except Exception as e:
        print(f"Edmunds error: {str(e)}")
        return None

def search_autolist(make, model=None):
    try:
        url = f"https://www.autolist.com/{make}"
        if model:
            url += f"-{model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'class': 'listing-link'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.autolist.com" + link_element['href']
        return {'source': 'Autolist', 'link': link}
    except Exception as e:
        print(f"Autolist error: {str(e)}")
        return None

def search_autonation(make, model=None):
    try:
        url = f"https://www.autonation.com/cars-for-sale/{make}"
        if model:
            url += f"/{model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'data-cmp': 'inventory-vehicle-link'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.autonation.com" + link_element['href']
        return {'source': 'AutoNation', 'link': link}
    except Exception as e:
        print(f"AutoNation error: {str(e)}")
        return None

def search_cargurus(make, model=None):
    try:
        url = f"https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sourceContext=carGurusHomePageModel&entitySelectingHelper.selectedEntity=d7&zip=90210#resultsPage=1"
        if model:
            url += f"&entitySelectingHelper.selectedEntity2=d1655"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'class': 'vO42pn'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.cargurus.com" + link_element['href']
        return {'source': 'CarGurus', 'link': link}
    except Exception as e:
        print(f"CarGurus error: {str(e)}")
        return None

def search_shift(make, model=None):
    try:
        url = f"https://shift.com/cars/{make}"
        if model:
            url += f"/{model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'class': 'inventory-card'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://shift.com" + link_element['href']
        return {'source': 'Shift', 'link': link}
    except Exception as e:
        print(f"Shift error: {str(e)}")
        return None

def search_vroom(make, model=None):
    try:
        url = f"https://www.vroom.com/inventory/{make}"
        if model:
            url += f"/{model}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'class': 'inventory-card'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.vroom.com" + link_element['href']
        return {'source': 'Vroom', 'link': link}
    except Exception as e:
        print(f"Vroom error: {str(e)}")
        return None

def search_hertz(make, model=None):
    try:
        url = f"https://www.hertzcarsales.com/used-cars-for-sale.htm?make={make.capitalize()}"
        if model:
            url += f"&model={model.capitalize()}"
            
        response = make_request(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        link_element = soup.find('a', {'class': 'vehicle-card-link'})
        if not link_element:
            raise ValueError("No car links found")
            
        link = "https://www.hertzcarsales.com" + link_element['href']
        return {'source': 'Hertz Car Sales', 'link': link}
    except Exception as e:
        print(f"Hertz error: {str(e)}")
        return None

# Main search function with all 13 platforms
def find_car(make="toyota", model=None):
    sites = [
        search_carmax,  # Moved to first position for priority
        search_autotrader,
        search_carscom,
        search_usnews,
        search_carvana,
        search_truecar,
        search_edmunds,
        search_autolist,
        search_autonation,
        search_cargurus,
        search_shift,
        search_vroom,
        search_hertz
    ]
    
    print(f"🔍 Searching for {make.upper()}{f' {model.upper()}' if model else ''} across {len(sites)} platforms...")
    
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(lambda f: f(make, model), sites))
    
    valid_results = [r for r in results if r]
    
    # Prioritize CarMax results by moving them to the front
    carmax_results = [r for r in valid_results if r['source'] == 'CarMax']
    other_results = [r for r in valid_results if r['source'] != 'CarMax']
    prioritized_results = carmax_results + other_results
    
    if prioritized_results:
        print(f"\n✅ Found {len(prioritized_results)} listings (CarMax prioritized):")
        for result in prioritized_results:
            print(f"{result['source']}: {result['link']}")
        return prioritized_results[0]['link']  # Always return CarMax first if available
    else:
        print("❌ No listings found across all platforms")
        return None
if __name__ == "__main__":
    car_link = find_car(make="bmw")
    if car_link:
        print(f"\nQuick link: {car_link}")
