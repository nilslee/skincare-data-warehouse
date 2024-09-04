import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

def download_pdf(driver, url, output_path):
    # Set up headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36',
        'Referer': 'https://www.google.com/',  # Example referer, change as needed
    }
    session = requests.Session()
    response = session.get(url, headers=headers, allow_redirects=True)
    
    # Capture the final redirected URL
    final_url = response.url
    print(final_url)
    # Download the PDF from the final URL
    with open(output_path, 'wb') as file:
        file.write(response.content)
        
    return final_url

output_dir = "/Users/aaronlee/Workspace/UTCS/DataWarehouse/webscrape/pdfs"

# Set up the options for headless mode if you don't want to open the browser window
chrome_options = Options()
# chrome_options.add_argument("--headless")

# Provide the path to your ChromeDriver
service = Service('/opt/homebrew/bin/chromedriver')

# Initialize the WebDriver
driver = uc.Chrome(service=service, options=chrome_options)
driver.get('https://www.aocd.org/page/DiseaseDatabaseHome')

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'td[style="vertical-align: top;"]'))
)

# Find elements and extract text
table_data = driver.find_elements(By.CSS_SELECTOR, 'td[style="vertical-align: top;"]')
for td in table_data:
    links = td.find_elements(By.TAG_NAME, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href and href.endswith('.pdf'):
            # print(f"Attempting to download: {href}")
            file_name = os.path.join(output_dir, href.split("/")[-1])
            download_pdf(driver, href, file_name)
        time.sleep(1)

# Close the driver
driver.quit()
