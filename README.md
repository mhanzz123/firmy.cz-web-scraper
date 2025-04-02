# firmy.cz-web-scraper
Python-based web scraper that collects business leads (name, website, email, IČO) from Czech search results using Selenium and exports them to a clean Excel file.
# Business Lead Scraper 🇨🇿

This is a Python web scraping tool that extracts business information from [firmy.cz](https://www.firmy.cz) based on any custom search query. It collects data like company name, website, email, and IČO, then exports it into a neatly formatted Excel sheet.

## ✅ Features
- Automates multi-page search result browsing
- Extracts details from each firm’s profile page
- Handles Seznam’s cookie consent page
- Skips duplicates and empty pages
- Saves data into Excel using `pandas` and `openpyxl`

## 📦 Tech Stack
- Python 3
- Selenium
- WebDriver Manager
- Pandas
- OpenPyXL

## 🚀 How to Use
1. Install dependencies:
```bash
pip install selenium pandas openpyxl webdriver-manager

2. Run the script:

python scraper.py

3. Enter your search query (e.g., estetická klinika brno)
The scraper will export an Excel file named estetická_klinika_brno.xlsx.
