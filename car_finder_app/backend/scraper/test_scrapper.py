# test_scraper.py
from webscrape_cars import (
    search_autotrader,
    search_carmax,
    search_carscom,
    search_carvana,
    search_truecar,
    search_edmunds,
    find_car
)

def test_individual_scrapers():
    test_make = "bmw"
    
    print("=== Testing Individual Scrapers ===")
    
    print("\nTesting AutoTrader...")
    autotrader_result = search_autotrader(test_make)
    print(f"Result: {autotrader_result}")
    
    print("\nTesting CarMax...")
    carmax_result = search_carmax(test_make)
    print(f"Result: {carmax_result}")
    
    print("\nTesting Cars.com...")
    carscom_result = search_carscom(test_make)
    print(f"Result: {carscom_result}")
    
    print("\nTesting Carvana...")
    carvana_result = search_carvana(test_make)
    print(f"Result: {carvana_result}")
    
    print("\nTesting TrueCar...")
    truecar_result = search_truecar(test_make)
    print(f"Result: {truecar_result}")
    
    print("\nTesting Edmunds...")
    edmunds_result = search_edmunds(test_make)
    print(f"Result: {edmunds_result}")

def test_full_search():
    test_make = "tesla"
    
    print("\n=== Testing Full Search Function ===")
    print(f"Searching for {test_make.upper()} across all platforms...")
    full_result = find_car(test_make)
    print(f"Final result: {full_result}")

if __name__ == "__main__":
    test_individual_scrapers()
    test_full_search()