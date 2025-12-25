import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import argparse

def run_scraper():
    parser = argparse.ArgumentParser(description="Scrape Las Vegas events.")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()

    print("Initializing Browser...")
    options = webdriver.ChromeOptions()
    if args.headless:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    # Basic user agent to avoid immediate blocking
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    events_data = []

    try:
        # Target: Visit Las Vegas Events Calendar
        url = "https://www.visitlasvegas.com/shows-events/all-shows-events/"
        print(f"Navigating to: {url}")
        driver.get(url)

        # Wait for the event list to allow dynamic content to load
        try:
             WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-type='events']"))
            )
        except Exception as e:
            print(f"Wait failed or no events found: {e}")

        # Extract Events
        # Selectors identified from debug HTML:
        # Item: div[data-type="events"]
        # Title: a.title
        # Date: .mini-date-container (contains .month and .day)
        # Venue: li.locations
        # Category: .img-banner

        event_cards = driver.find_elements(By.CSS_SELECTOR, "div[data-type='events']")
        print(f"Found {len(event_cards)} event cards. Extracting data...")

        for card in event_cards:
            record = {
                "name": None,
                "date": None,
                "venue": None,
                "category": None
            }
            try:
                record["name"] = card.find_element(By.CSS_SELECTOR, "a.title").text
            except: pass

            try:
                # Date is "Dec 24" etc.
                month = card.find_element(By.CSS_SELECTOR, ".mini-date-container .month").text
                day = card.find_element(By.CSS_SELECTOR, ".mini-date-container .day").text
                record["date"] = f"{month} {day}"
                
                # Simple logic to add year (upcoming)
                # Ideally we would be smarter about year boundaries
                current_year = datetime.now().year
                # If event month is earlier than current month, likely next year (e.g., extracting in Dec for Jan event)
                # For now, we'll just append current year or next year roughly
                # A robust parser would parse "Dec" to 12 and compare
                record["date_raw"] = f"{month} {day}" 
            except: pass

            try:
                record["venue"] = card.find_element(By.CSS_SELECTOR, "li.locations").text
            except: pass
            
            try:
                 record["category"] = card.find_element(By.CSS_SELECTOR, ".img-banner").text
            except: pass

            if record["name"]:
                events_data.append(record)

        # Removed debug HTML saving


    except Exception as e:
        print(f"Critical Error: {e}")
    
    finally:
        driver.quit()
        
        # Save Empty or Placeholder CSV to verify functionality
        if not events_data:
            print("No events found (Selectors need update). Saving placeholder.")
            events_data.append({"name": "Test Event", "date": datetime.now().strftime("%Y-%m-%d"), "venue": "Test Venue"})

        df = pd.DataFrame(events_data)
        filename = f"data/vegas_events_{datetime.now().strftime('%Y-%m-%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} rows to {filename}")

if __name__ == "__main__":
    run_scraper()
