# 🏪 BestBuy Store Scraper

This Python script automates the extraction of store data from [BestBuy’s Store Locator](https://www.bestbuy.com/site/store-locator). It uses Selenium to interact with the UI and then calls an **internal API** to fetch detailed services offered at each store.

---

## 📦 Features

- ZIP-based store search with Selenium
- Full scraping of store cards from the locator UI
- Extraction of store metadata: name, address, URL
- Internal **API usage to get store services**
- Saves all data to a structured CSV

---

## 🧠 Scraping Logic

### 1. 🔍 Search Automation

- Opens the store locator page using Selenium
- Enters a ZIP code (e.g., `10001`) in the search bar
- Clicks the `Update` button to trigger a results reload
- Waits until store cards appear

### 2. 🧾 Store Card Extraction

- For each `<li class="store" ...>` tag:
  - Extracts:
    - `store_id` from the `data-store-id` attribute
    - `business_name` from the `<button data-cy="store-heading">`
    - `street_address` from nested `<span class="loc-address">`
    - `URL` from the `<a class="details">` tag

### 3. 🔌 Internal API Usage

After collecting all `store_id`s, the script makes a batch request to this **BestBuy internal API**:

```
https://www.bestbuy.com/api/tcfb/model.json
```

With query parameters:

```python
params = {
    "paths": json.dumps([
        ["shop", "magellan", "v2", "storeId", "stores", [482, 1028, 835, ...], "services"]
    ]),
    "method": "get"
}
```

**⚙️ Key Concepts:**

| Element         | Description                                      |
|----------------|--------------------------------------------------|
| `shop/magellan/v2/storeId/stores` | API namespace for store services         |
| `[store_ids]`   | List of numeric store IDs (int, not str)         |
| `"services"`    | Attribute to request service types per store     |

📌 **Example full request:**

```
https://www.bestbuy.com/api/tcfb/model.json?paths=[[ "shop", "magellan", "v2", "storeId", "stores", [482,1172], "services" ]]&method=get
```

**Response:**

```json
{
  "jsonGraph": {
    "shop": {
      "magellan": {
        "v2": {
          "storeId": {
            "stores": {
              "482": {
                "services": {
                  "value": ["Apple Shop", "Geek Squad Services", ...]
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## 🧹 Data Cleaning

- Invisible characters (`\u200f`, `\ufeff`, etc.) are removed using regex
- `materials_accepted` (i.e., services) is flattened into a comma-separated string for CSV

---

## ⚠️ Error Handling

- Wraps scraping and API calls in `try/except`
- Catches:
  - Element not found errors
  - Interception errors (`ElementClickInterceptedException`)
  - 403 Forbidden errors from API
- Gracefully logs errors and continues execution

---

## 📤 Output CSV Format

Saves output in `bestbuy_data.csv`:

| business_name           | street_address                        | URL                             | materials_accepted                             |
|-------------------------|----------------------------------------|----------------------------------|------------------------------------------------|
| Chelsea (23rd and 6th)  | 60 W 23rd St, New York, NY 10010       | https://stores.bestbuy.com/482   | Apple Shop, Geek Squad Services, Trade-In ... |

---

## 🛠️ Requirements

Install dependencies:

```bash
pip install selenium beautifulsoup4 requests
```

Also ensure:

- **Brave or Chrome browser installed**
- **Matching WebDriver** added to system PATH
- Adjust `chrome_options.binary_location` if not using Chrome

---

## 🚀 Usage

1. Edit the ZIP code in `main` block:

```python
pincode = 10001
```

2. Run the script:

```bash
python3 bestbuy_scrapping.py
```

3. Output file: `bestbuy_data.csv`

---
