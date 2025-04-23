import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager




def selenium_crawler(url):
    """
    Crawler using Selenium for JavaScript-rendered content
    """
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load (you can adjust the time as needed)
        time.sleep(3)
        
        # Get the page source after JavaScript has been executed
        page_source = driver.page_source
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Example: Extract the title
        title = soup.title.text if soup.title else "No title found"
        print(f"Page title (Selenium): {title}")
        
        # Example: Find elements by class name
        # Replace 'example-class' with the actual class you want to find
        elements = driver.find_elements(By.CLASS_NAME, 'example-class')
        print(f"Found {len(elements)} elements with class 'example-class'")
        
        # Example: Extract text from the found elements
        for i, element in enumerate(elements[:3]):  # Show first 3 elements
            print(f"Element {i+1} text: {element.text.strip()}")
    
    finally:
        # Always close the driver
        driver.quit()


if __name__ == "__main__":
    # Example URL - replace with your target website
    target_url = "https://example.com"

    
    print("\n=== Selenium Crawler ===")
    selenium_crawler(target_url) 