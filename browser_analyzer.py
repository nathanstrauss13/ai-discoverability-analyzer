import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

def fetch_with_browser(url, wait_time=5):
    """Fetch webpage content using a real browser to bypass anti-bot measures."""
    
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set a realistic user agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    try:
        # Initialize the driver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the page to load
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Additional wait for JavaScript rendering
        time.sleep(2)
        
        # Get the page source
        html_content = driver.page_source
        
        # Close the driver
        driver.quit()
        
        return html_content
        
    except Exception as e:
        print(f"Browser fetch error: {e}")
        if 'driver' in locals():
            driver.quit()
        return None

def analyze_with_browser(url):
    """Analyze a webpage using browser automation to bypass anti-bot protection."""
    
    print(f"Fetching {url} with browser automation...")
    html_content = fetch_with_browser(url)
    
    if html_content:
        # Use the existing analysis logic
        from app import analyze_webpage_structure
        analysis = analyze_webpage_structure(html_content, url)
        return analysis
    else:
        return None

# Example usage
if __name__ == "__main__":
    # Test with sites that block regular requests
    test_urls = [
        "https://www.signetjewelers.com/sustainability/report/default.aspx",
        "https://www.brilliantearth.com"
    ]
    
    for url in test_urls:
        print(f"\nAnalyzing: {url}")
        result = analyze_with_browser(url)
        if result:
            print(f"Success! Found {len(result['headings']['h1'])} H1 tags")
        else:
            print("Failed to analyze")
