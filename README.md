# Earth911 Electronics Recycling Scraper

This project scrapes electronics recycling facility data from the [Earth911](https://search.earth911.com/) website for a specified ZIP code and saves it into a structured CSV file.

## 📌 Features

- Scrapes business names, addresses, URLs, last update dates, and accepted materials
- Handles multiple pages (pagination)
- Uses a headless browser (Selenium + Chrome)
- Performs HTML parsing using BeautifulSoup
- Includes basic error handling and data cleaning
- Outputs structured data into `earth911_data.csv`

## 🔁 Scraping Logic

1. **Pagination Loop**
   - Starts with `page=1` and continues until a maximum page number is reached (currently `page < 3`) or no results are returned.
   - Dynamically constructs URLs using the page number and predefined search parameters for electronics recycling in New York (ZIP 10001).

2. **Company List Extraction (`scrap_page`)**
   - Opens the results page with Selenium.
   - Waits until listing elements (`li.result-item`) load.
   - Extracts:
     - Business name and page link
     - Street address components (`address1`, `address2`, `address3`) and merges them cleanly.

3. **Company Details Extraction (`get_company_data`)**
   - Visits each company’s detail page.
   - Scrapes:
     - `last_update_date` from `<span class="last-verified">`
     - Materials accepted from each `<td class="material-name">` (skipping header row)

4. **Data Structuring and CSV Export**
   - Collects all entries page-wise in a dictionary.
   - Writes a flattened structure to `earth911_data.csv` with headers:
     - `business_name`, `last_update_date`, `street_address`, `materials_accepted`, `url`

## 🧹 Data Cleaning

- Uses `clean_text()` to strip:
  - Unicode characters like `\ufeff`, `\u200b`, etc.
  - Extra whitespace and line breaks from strings.
- Materials accepted are joined as a comma-separated string.

## ⚠️ Error Handling

- If any exception occurs while scraping a page or details:
  - Prints the error (`Error page:`, `Error get:`)
  - Returns `None` gracefully and skips that entry.
- Browser session is always terminated with `driver.quit()` in `finally` blocks.

## 🛠️ Dependencies

Ensure the following Python packages are installed:

```bash
pip install selenium beautifulsoup4
