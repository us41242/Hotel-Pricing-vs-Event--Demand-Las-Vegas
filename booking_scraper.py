import time
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_next_weekend():
    """
    Calculates the dates for the upcoming Friday (Check-in) 
    and Sunday (Check-out).
    """
    today = datetime.now()
    # 0 = Monday, 4 = Friday. 
    # (4 - today.weekday() + 7) % 7 calculates days until next Friday.
    days_until_friday = (4 - today.weekday() + 7) % 7
    if days_until_friday == 0:
        days_until_friday = 7 # If today is Friday, look to next week
        
    next_friday = today + timedelta(days=days_until_friday)
    next_sunday = next_friday + timedelta(days=2)
    
    return next_friday.strftime("%Y-%m-%d"), next_sunday.strftime("%Y-%m-%d")

def run_scraper():
    # 1. Setup Dates
    checkin_date, checkout_date = get_next_weekend()
    print(f"--- Target Weekend: {checkin_date} to {checkout_date} ---")

    # 2. Setup Browser
    print("Initializing Browser...")
    options = webdriver.ChromeOptions()
    # Uncomment to run in headless mode # options.add_argument("--headless") 

    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    hotel_data = [] # List to store our data

    try:
        # 3. Navigate to Booking.com Search Results for Las Vegas
        base_url = "https://www.booking.com/searchresults.html"
        city = "Las Vegas"
        
        search_url = (
            f"{base_url}?ss={city}"
            f"&checkin={checkin_date}"
            f"&checkout={checkout_date}"
            f"&group_adults=2"
            f"&no_rooms=1"
            f"&group_children=0"
        )
        
        print(f"Navigating to: {search_url}")
        driver.get(search_url)

        # 4. Handle Potential Popups
        try:
            print("Checking for popups...")
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Dismiss sign-in info.']"))
            )
            close_button.click()
            print("Popup closed.")
        except:
            print("No popup found (or couldn't close it). Continuing...")

        # 5. Wait for Hotel Listings to Load
        print("Waiting for hotel list to load...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="property-card"]'))
        )
        print("Hotel list loaded.")

        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        hotels = driver.find_elements(By.CSS_SELECTOR, '[data-testid="property-card"]')
        print(f"Found {len(hotels)} hotels. Extracting data...")

        for hotel in hotels:
            # We use a dictionary for each hotel so we can easily save to CSV later
            record = {
                'name': None,
                'price': None,
                'rating': None,
                'review_count': None,
                'distance': None,
                'date_scraped': datetime.now().strftime("%Y-%m-%d")
            }
            
            # Extract Data with Error Handling
            try:
                record['name'] = hotel.find_element(By.CSS_SELECTOR, '[data-testid="title"]').text
            except: pass

            try:
                record['price'] = hotel.find_element(By.CSS_SELECTOR, '[data-testid="price-and-discounted-price"]').text
            except: pass

            try:
                #  Targets "8.8 Fabulous"
                record['rating'] = hotel.find_element(By.CSS_SELECTOR, '[data-testid="reviewer-score"]').text.split()[0]
            except: pass
            
            try:
                #  Targets "1234 reviews"
                record['review_count'] = hotel.find_element(By.CSS_SELECTOR, '[data-testid="review-score"] div:nth-child(2)').text
            except: pass
                # Distance from center or landmark
            try:
                record['distance'] = hotel.find_element(By.CSS_SELECTOR, '[data-testid="distance"]').text
            except: pass
            
            # Only add record if we have a hotel name
            if record['name']:
                hotel_data.append(record)

    except Exception as e:
        print(f"Critical Error: {e}")
        
    finally:
        driver.quit()
        
        # SAVE TO CSV
        if hotel_data:
            df = pd.DataFrame(hotel_data)
            # Create a filename with today's date
            filename = f"data/vegas_hotels_{datetime.now().strftime('%Y-%m-%d')}.csv"
            df.to_csv(filename, index=False)
            print(f"SUCCESS: Saved {len(df)} rows to {filename}")
            print(df.head()) # Show first 5 rows in terminal
        else:
            print("No data found.")

if __name__ == "__main__":
    run_scraper()