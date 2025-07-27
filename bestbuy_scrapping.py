import csv
from bs4 import BeautifulSoup
import time
import random
import re
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

chrome_options.binary_location = "/usr/bin/brave-browser"  #comment if using chrome


def scrap_Store_IDs(pincode):
    url = 'https://www.bestbuy.com/site/store-locator'
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    try:
        driver.refresh()
        wait = WebDriverWait(driver, 10)
        zip_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.zip-code-input")))
        zip_input.clear()
        zip_input.send_keys(pincode)

        #scrolling to get button in view
        update_button = driver.find_element(By.CSS_SELECTOR, "button.location-zip-code-form-update-btn")
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", update_button)
        time.sleep(1)
        update_button.click()

        time.sleep(random.uniform(3, 6))
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Get all store cards
        store_tags = soup.find_all("li", {"class": "store"})
        if not store_tags:
            return {"error": "No store found for this pincode"}

        #getting card details
        store_ids = {}
        for store in store_tags:
            store_id = int(store.get("data-store-id"))
            company_name = store.find("button", {"data-cy": "store-heading"}).text.strip()
            address_block = store.find("span", {"class": "loc-address"})
            street = address_block.find_all("span")[0].text.strip()
            extended = address_block.find_all("span")[1].text.strip()
            address = f"{street}, {extended}"
            store_link = store.find("a", class_="details")["href"]
            
            store_ids[store_id]={
                "business_name": company_name,
                "street_address": address,
                "URL": store_link
            }
        return store_ids
    
    except Exception as e:
        print(f"Error scrap: {e}")
        return None
    
    finally:
        driver.quit()


def clean_text(text):
    return re.sub(r'[\u200b\u200e\u200f\ufeff]', '', text).strip()

def get_store_services(store_ids):

    if not store_ids or not all(isinstance(x, int) for x in store_ids):
        raise ValueError("store_ids must be a non-empty list of integers")

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Host": "www.bestbuy.com",
        "Referer": "https://www.bestbuy.com/site/store-locator",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:141.0) Gecko/20100101 Firefox/141.0"
    }

    # Construct the API URL
    base_url = "https://www.bestbuy.com/api/tcfb/model.json"
    paths = [["shop", "magellan", "v2", "storeId", "stores", store_ids, "services"]]
    params = {
        "paths": json.dumps(paths),
        "method": "get"
    }

    print("Requesting URL:", base_url + "?" + requests.compat.urlencode(params))

    try:
        services_by_store = {}

        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        data = response.json()
        
        try:
            stores = data.get("jsonGraph", {}).get("shop", {}).get("magellan", {}).get("v2", {}).get("storeId", {}).get("stores", {})
            if not stores:
                print("Warning: No store data found in response")
                return services_by_store

            for store_id, store_info in stores.items():
                services = store_info.get("services", {}).get("value", [])
                services_by_store[int(store_id)] = services

            return services_by_store

        except KeyError as e:
            print(f"Error accessing response data: Missing key {e}")
            return None

    except Exception as e:
        print(f"Error in API url: {e}")
        return None

if __name__=="__main__":
    # pincode=10001
    # data=scrap_Store_IDs(pincode)
    # print(data, type(data))
    # ids=list(data.keys())
    # print(ids)
    # data2=get_store_services(ids)
    # for id, value in data.items():
    #     value.update({'materials_accepted':data2[id]})
    # # print(data)
    data={482: {'business_name': 'Chelsea (23rd and 6th)', 'street_address': '60 W 23rd St, New York, NY 10010', 'URL': 'https://stores.bestbuy.com/482', 'materials_accepted': ['Alienware Experience Shop', 'Apple Shop', 'Geek Squad Services', 'Premium Home Theater', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Samsung Experience Shop', 'Trade-In']}, 1028: {'business_name': 'Midtown Manhattan (44th and 5th)', 'street_address': '531 5th Ave, New York, NY 10017', 'URL': 'https://stores.bestbuy.com/1028', 'materials_accepted': ['Apple Authorized Service Provider', 'Apple Shop', 'Camera Experience Shop', 'Geek Squad Services', 'Premium Design Center', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Samsung Experience Shop', 'Trade-In']}, 1531: {'business_name': 'Union Square', 'street_address': '52 E 14th St, Number 64', 'URL': 'https://stores.bestbuy.com/1531', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Authorized Service Provider', 'Alienware Experience Shop', 'Apple Shop', 'Camera Experience Shop', 'Best Buy Fit Program', 'Geek Squad Services', 'Google Home Experience', 'Hearing Solutions Center', 'LG Experience', 'Premium Home Theater', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Samsung Experience Shop', 'Sony Experience', 'Trade-In']}, 1535: {'business_name': 'Jersey City', 'street_address': '125 18th St, Jersey City, NJ 07310', 'URL': 'https://stores.bestbuy.com/1535', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Shop', 'Geek Squad Services', 'Google Home Experience', 'Hearing Solutions Center', 'LG Experience', 'Premium Home Theater', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Sony Experience', 'Trade-In']}, 835: {'business_name': '86th and Lexington', 'street_address': '1280 Lexington Ave, New York, NY 10028', 'URL': 'https://stores.bestbuy.com/835', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Shop', 'Geek Squad Services', 'Google Home Experience', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Samsung Experience Shop', 'Trade-In']}, 474: {'business_name': 'Secaucus', 'street_address': '3 Mill Creek Dr, Secaucus, NJ 07094', 'URL': 'https://stores.bestbuy.com/474', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Authorized Service Provider', 'Apple Shop', 'Geek Squad Services', 'Google Home Experience', 'Hearing Solutions Center', 'LG Experience', 'Premium Design Center', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Sony Experience', 'Trade-In']}, 478: {'business_name': 'Long Island City', 'street_address': '5001 Northern Blvd, Long Island City, NY 11101', 'URL': 'https://stores.bestbuy.com/478', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Authorized Service Provider', 'Apple Shop', 'Geek Squad Services', 'Google Home Experience', 'Hearing Solutions Center', 'LG Experience', 'Premium Home Theater', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Samsung Experience Shop', 'Sony Experience', 'Samsung Open House', 'Trade-In']}, 2518: {'business_name': 'Atlantic Center', 'street_address': '625 Atlantic Ave, Ste A7', 'URL': 'https://stores.bestbuy.com/2518', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Shop', 'Geek Squad Services', 'Google Home Experience', 'Hearing Solutions Center', 'Premium Home Theater', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Trade-In']}, 1217: {'business_name': 'American Dream', 'street_address': '1 American Dream Way, C351', 'URL': 'https://stores.bestbuy.com/1217', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Shop', 'Camera Experience Shop', 'Best Buy Fit Program', 'Geek Squad Services', 'Google Home Experience', 'Lovesac Experience', 'Microsoft Windows Store', 'Samsung Open House', 'Trade-In', 'Total Tech Support']}, 1172: {'business_name': 'Bronx Terminal Market', 'street_address': '610 Exterior St, Bronx, NY 10451', 'URL': 'https://stores.bestbuy.com/1172', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Authorized Service Provider', 'Apple Shop', 'Geek Squad Services', 'Google Home Experience', 'Microsoft Windows Store', 'Trade-In']}, 483: {'business_name': 'Rego Park', 'street_address': '6135 Junction Blvd, Rego Park, NY 11374', 'URL': 'https://stores.bestbuy.com/483', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Shop', 'Camera Experience Shop', 'Dyson Demo Experience', 'Geek Squad Services', 'Google Home Experience', 'Hearing Solutions Center', 'Car and GPS Install Services', 'LG Experience', 'Premium Home Theater', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Samsung Experience Shop', 'Sony Experience', 'Trade-In']}, 1886: {'business_name': 'Gateway Brooklyn', 'street_address': '369 Gateway Dr, Brooklyn, NY 11239', 'URL': 'https://stores.bestbuy.com/1886', 'materials_accepted': ['Apple Authorized Service Provider', 'Apple Shop', 'Geek Squad Services', 'Hearing Solutions Center', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Trade-In']}, 1261: {'business_name': 'Bronx Riverdale', 'street_address': '171 W 230th St, Ste 103', 'URL': 'https://stores.bestbuy.com/1261', 'materials_accepted': ['Geek Squad Services', 'Trade-In']}, 599: {'business_name': 'Bay Parkway Brooklyn', 'street_address': '8923 Bay Pkwy, Brooklyn, NY 11214', 'URL': 'https://stores.bestbuy.com/599', 'materials_accepted': ['Amazon Alexa Experience', 'Apple Authorized Service Provider', 'Apple Shop', 'Camera Experience Shop', 'Geek Squad Services', 'Google Home Experience', 'Hearing Solutions Center', 'LG Experience', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Samsung Experience Shop', 'Sony Experience', 'Trade-In']}, 887: {'business_name': 'Bergen Town Center', 'street_address': '2400 Bergen Town Ctr, Paramus, NJ 07652', 'URL': 'https://stores.bestbuy.com/887', 'materials_accepted': ['Apple Shop', 'Geek Squad Services', 'LG Experience', 'Premium Home Theater', 'Microsoft Windows Store', 'Samsung Entertainment Experience', 'Samsung Experience Shop', 'Sony Experience', 'Trade-In']}}

    head=["Business_name","Street_address","URL","Materials_accepted"]
    with open("bestbuy_data.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=head)
        writer.writeheader()

        for store in data.values():
            writer.writerow({
                "Business_name": store["business_name"],
                "Street_address": store["street_address"],
                "Materials_accepted": ", ".join(store["materials_accepted"]),
                "URL": store["URL"]
            })

    print("CSV file 'bestbuy_data.csv' saved successfully.")