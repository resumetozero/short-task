from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import re
import json
import random

# --- Setup headless browser ---
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
# chrome_options.binary_location = "/usr/bin/brave-browser"


def clean_text(text):
    return re.sub(r'[\u200b\u200e\u200f\ufeff]', '', text).strip()

def scrap_page(url):
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(random.uniform(2,5))
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "result-item"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all("li",class_="result-item")
        # print(soup)
        companies=[]
        for item in items:
            company = {}
            
            # Extract title and link
            title_elem = item.find('h2', class_='title')
            if title_elem and title_elem.a:
                company['title'] = clean_text(title_elem.a.get_text(strip=True))
                company['link'] = f"https://search.earth911.com{title_elem.a['href']}" 
            
            # Extract address
            contact = item.find('div', class_='contact')
            if contact:
                address_parts = []
                address1 = contact.find('p', class_='address1').get_text(strip=True)
                address2 = contact.find('p', class_='address2').get_text(strip=True)
                address3 = contact.find('p', class_='address3').get_text(strip=True)
                
                # Combine address parts, ignoring empty ones
                if address1:
                    address_parts.append(clean_text(address1))
                if address2:
                    address_parts.append(clean_text(address2))
                if address3:
                    address_parts.append(clean_text(address3))
                
                company['address'] = ', '.join(address_parts)
            
            companies.append(company)
        driver.quit()
        return companies
        
    except Exception as e:
        print(f"Error page :{e}")
        return None
    
    finally:
        driver.quit()
    
def get_company_data(url):
    material_accepted=[]
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(random.uniform(2,5))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        h1 = soup.find("h1", class_="back-to noprint")
        if h1:
            span = h1.find("span", class_="last-verified")
            if span:
                last_update = span.get_text(strip=True)
            else:
                last_update = None

        material_td = soup.find_all("td", class_="material-name")
        if material_td:
            for m in material_td[1:]:
                material_accepted.append(clean_text(m.get_text(strip=True)))
        else:
            material_accepted=None
        return {
            "last_update_date": last_update,
            "material_accepted": material_accepted
        }

    
    except Exception as e:
        print(f"Error get :{e}")
        return None
    
    finally:
        driver.quit()


if __name__=="__main__":
    data={}
    page=1
    while page<3:
        url=f"https://search.earth911.com/?what=Electronics&where=10001&max_distance=100&country=US&province=NY&city=New+York&region=New+York&postal_code=10001&latitude=40.74807084035&longitude=-73.99234262099&sponsor=&list_filter=all&page={page}"
        print(page)
        data[page]=scrap_page(url)
        if not scrap_page(url):
            break
        page+=1
    # print(data)
    for page_num,company in data.items():
        for i in range(len(company)):
            data2=get_company_data(company[i]['link'])
            # print(data2, type(data2))
            data[page_num][i]["last_update_date"]= data2["last_update_date"]
            data[page_num][i]["material_accepted"]= data2["material_accepted"]
    # print(data)

    head=['business_name','last_update_date','street_address','materials_accepted','url']
    with open("earth911_data.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=head)
        writer.writeheader()

        for page_data in data.values():
            for entry in page_data:
                writer.writerow({
                    "business_name": entry["title"],
                    "last_update_date": entry["last_update_date"],
                    "street_address": entry["address"],
                    "materials_accepted": ", ".join(entry["material_accepted"]),
                    "url": entry["link"]
                })

    print("CSV file 'earth911_data.csv' saved successfully.")






