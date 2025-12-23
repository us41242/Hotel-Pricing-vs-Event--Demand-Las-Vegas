import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def run_test():
    print("Initializing browser...")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    url = "https://www.booking.com"
    print(f"Navigating to {url}...")
    driver.get(url)
    
    time.sleep(3)
    
    print("Page Title is:", driver.title)
    
    # driver.quit() # Uncomment this later to close the browser after testing
    print("Test Complete! Browser is open.")

if __name__ == "__main__":
    run_test()