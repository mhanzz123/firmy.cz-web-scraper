from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from urllib.parse import quote_plus
from collections import Counter

def setup_browser():
    options = Options()
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def collect_all_firm_links(browser, query):
    encoded = quote_plus(query)
    firm_urls = []
    page_number = 1

    while True:
        url = f"https://www.firmy.cz/?q={encoded}" if page_number == 1 else f"https://www.firmy.cz/?q={encoded}&page={page_number}"
        print(f"📄 Visiting search results page {page_number}: {url}")
        browser.get(url)

        try:
            time.sleep(2)  # Give it time to settle
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'a.companyTitle.statCompanyDetail'))
            )

            elements = browser.find_elements(By.CSS_SELECTOR, 'a.companyTitle.statCompanyDetail')
            new_links = [el.get_attribute("href") for el in elements if el.get_attribute("href")]

            # 🛑 Stop if page has no results or duplicates only
            unique_new = [url for url in new_links if url not in firm_urls]
            if not unique_new:
                print("🛑 No new firm links found, pagination ends here.")
                break

            firm_urls.extend(unique_new)
            print(f"➕ Added {len(unique_new)} links (Total: {len(firm_urls)})")

            page_number += 1
            time.sleep(1)

        except Exception as e:
            print(f"❌ Pagination failed: {e}")
            break

    return firm_urls

def extract_company_data(browser):
    try:
        name = browser.find_element(By.CSS_SELECTOR, 'h1.detailPrimaryTitle.speakable.title').text.strip()
    except:
        name = browser.title.strip()

    try:
        web_el = browser.find_element(By.CSS_SELECTOR, 'a.detailWebUrl.url.companyUrl')
        website = web_el.text.strip() or web_el.get_attribute("href")
    except:
        website = ''

    try:
        email = browser.find_element(By.CSS_SELECTOR, 'div.detailEmail a[href^="mailto:"]').get_attribute('href').replace("mailto:", "")
    except:
        email = ''

    try:
        ico_raw = browser.find_element(By.CSS_SELECTOR, 'div.detailBusinessInfo').text.strip()
        ico = ico_raw.split("Více")[0].strip()
    except:
        ico = ''

    return {
        'name': name,
        'website': website,
        'email': email,
        'ico': ico,
        'profile': browser.current_url
    }

def handle_seznam_consent(browser):
    try:
        if "cmp.seznam.cz" not in browser.current_url:
            return True
        print("🍪 On Seznam consent page. Click manually if needed.")
        input("🛑 Waiting for manual click — press ENTER when you’ve clicked Souhlasím... ")
        WebDriverWait(browser, 10).until_not(EC.url_contains("cmp.seznam.cz"))
        print("✅ Redirected to firm page")
        return True
    except Exception as e:
        print(f"❌ Consent click failed: {e}")
        return False

def scrape_firmy(query):
    browser = setup_browser()
    results = []

    try:
        firm_urls = collect_all_firm_links(browser, query)
        print(f"🔗 Collected {len(firm_urls)} firm profile URLs")

        for i, url in enumerate(firm_urls):
            print(f"➡️ Visiting firm #{i+1}: {url}")
            browser.get(url)
            if not handle_seznam_consent(browser):
                continue

            data = extract_company_data(browser)
            if data:
                print(f"✅ Scraped: {data['name']} | {data['ico']}")
                results.append(data)

    finally:
        browser.quit()

    # Save to Excel
    filename = query.replace(" ", "_") + ".xlsx"
    df = pd.DataFrame(results)
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Firmy")
        sheet = writer.sheets["Firmy"]
        for col in sheet.columns:
            max_length = max(len(str(cell.value)) for cell in col)
            col_letter = col[0].column_letter
            sheet.column_dimensions[col_letter].width = max_length + 3

    print(f"📄 Done! Results saved to {filename}")

if __name__ == "__main__":
    scrape_firmy("estetická klinika brno")
