import requests
import os
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
            response.raise_for_status()  
            soup = BeautifulSoup(response.text, 'html.parser')
            
            extracted_texts = {}

            
            location = soup.find('h4', class_='title')
           
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
            
            options = webdriver.ChromeOptions() 
            
            # https://stackoverflow.com/questions/78796828/i-got-this-error-oserror-winerror-193-1-is-not-a-valid-win32-application
            # ------
            options.headless = True 
            options.add_argument("--headless=new")
            
            chrome_install = ChromeDriverManager().install()

            folder = os.path.dirname(chrome_install)
            chromedriver_path = os.path.join(folder, "chromedriver.exe")

            service = ChromeService(chromedriver_path) 

            driver = webdriver.Chrome(service=service, options=options)
            # ------
            
            url = self.url
            
            driver.get(url) 
            wait = WebDriverWait(driver, 5)
            extracted_texts = {}
            elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.location-header')))
            time = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.text-muted')))
            
           
            for i, element in enumerate(elements):
                
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
            
            options = webdriver.ChromeOptions() 
            options.headless = True 
            options.add_argument("--headless=new")
            chrome_install = ChromeDriverManager().install()

            folder = os.path.dirname(chrome_install)
            chromedriver_path = os.path.join(folder, "chromedriver.exe")

            service = ChromeService(chromedriver_path) 

            driver = webdriver.Chrome(service=service, options=options)
            # service=ChromeService( 
            #     ChromeDriverManager().install()), options=options
            url = self.url
            
            driver.get(url) 
            wait = WebDriverWait(driver, 5)
            extracted_texts = []
            
            items = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.itemname')))
            
            for i, item in enumerate(items):
                
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
            
            options = webdriver.ChromeOptions() 
            
            
            options.headless = True 
            options.add_argument("--headless=new")
            
            chrome_install = ChromeDriverManager().install()

            folder = os.path.dirname(chrome_install)
            chromedriver_path = os.path.join(folder, "chromedriver.exe")

            service = ChromeService(chromedriver_path) 

            driver = webdriver.Chrome(service=service, options=options)
            
            
            
            url = self.url
            
            driver.get(url) 
            wait = WebDriverWait(driver, 5)
            extracted_texts = []
            costs = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.bullion')))
            
            for i, cost in enumerate(costs):
                
                full_text = cost.text
                
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



        