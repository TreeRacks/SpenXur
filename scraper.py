import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
class WebScraper:
    def __init__(self, url):
        self.url = url

    async def fetch_data(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')

            # Initialize a dictionary to store the extracted texts
            extracted_texts = {}

            # Find and extract text from multiple HTML elements
            location = soup.find('h4', class_='title')
           
            
            # Add the extracted text to the dictionary
            extracted_texts[''] = location.text if location else None
            exotic1 = soup.find('h4', class_='et_pb_module_header')
            
            extracted_texts['Exotic Weapon'] = exotic1.text if exotic1 else None
            exotics = soup.find_all('h4', class_='et_pb_module_header')
            hawkmoon = soup.find_all(class_='et_pb_blurb_description')
            extracted_texts['Hawkmoon'] = hawkmoon[1].text if hawkmoon[1] else None
            extracted_texts['Hunter Exotic Armor'] = exotics[2].text if exotics[2] else None
            extracted_texts['Titan Exotic Armor'] = exotics[3].text if exotics[3] else None
            extracted_texts['Warlock Exotic Armor'] = exotics[4].text if exotics[4] else None
            return extracted_texts

        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    async def fetch_minerva_data(self):
        try:
            # instantiate options 
            options = webdriver.ChromeOptions() 
            
            # run browser in headless mode 
            options.headless = True 
            options.add_argument("--headless=new")
            
            # instantiate driver 
            driver = webdriver.Chrome(service=ChromeService( 
                ChromeDriverManager().install()), options=options) 
            
            # load website 
            
            url = self.url
            # get the entire website content 
            driver.get(url) 
            wait = WebDriverWait(driver, 5)
            extracted_texts = {}
            # select elements by class name 
            # Wait until the elements with the class name 'location-header' are present
            elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.location-header')))
            time = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.text-muted')))
            
           
            for i, element in enumerate(elements):
                # Extract text within the element
                text = element.text
                #remove the last 3 characters
                text = text[:-3]
                
                extracted_texts['Location'] = text
            
            extracted_texts[''] = time.text
            
            return extracted_texts
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    async def fetch_minerva_inventory(self):
        try:
            # instantiate options 
            options = webdriver.ChromeOptions() 
            
            # run browser in headless mode 
            options.headless = True 
            options.add_argument("--headless=new")
            # instantiate driver 
            driver = webdriver.Chrome(service=ChromeService( 
                ChromeDriverManager().install()), options=options) 
            
            # load website 
            
            url = self.url
            # get the entire website content 
            driver.get(url) 
            wait = WebDriverWait(driver, 5)
            extracted_texts = []
            # select elements by class name 
            # Wait until the elements with the class name 'location-header' are present
            items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.itemname')))
            
            for i, item in enumerate(items):
                # Extract text within the element
                text = item.text
                #remove the last 3 characters
                # print (text)
                
                extracted_texts.append(text)
        
                    
            return extracted_texts
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    async def fetch_minerva_costs(self):

        try:
            # instantiate options 
            options = webdriver.ChromeOptions() 
            
            # run browser in headless mode 
            options.headless = True 
            options.add_argument("--headless=new")
            # instantiate driver 
            driver = webdriver.Chrome(service=ChromeService( 
                ChromeDriverManager().install()), options=options) 
            
            # load website 
            
            url = self.url
            # get the entire website content 
            driver.get(url) 
            wait = WebDriverWait(driver, 5)
            extracted_texts = []
            costs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.bullion')))
            
            for i, cost in enumerate(costs):
                # Extract the full text content of the div
                full_text = cost.text
                
                # Remove the text within the img tag
                try:
                    img_element = cost.find_element(By.TAG_NAME, 'img')
                    img_text = img_element.get_attribute('outerHTML')
                    text_without_img = full_text.replace(img_text, '').strip()
                except:
                    # If no img element is found, use the full text
                    text_without_img = full_text.strip()
                #only append if it is not ''
                if text_without_img != '':
                    extracted_texts.append(text_without_img)
                
            return extracted_texts
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None



        