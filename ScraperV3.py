import random
import time
import re
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, quote_plus

# from Scraper import TELEGRAM_CHAT_ID
# ONFIGURATION
BASE_URL = "https://www.sgcarmart.com/used-cars/listing"
PARAMS = {
    'dp2': '12000',
    'fr': '2016',
    'to': '2019',
    'cts[]': '18',
    'vts[]': ['12','13','9','10','11','8','7','3','2', '6'],
    'fue': 'Petrol',
    'opc[]': '0',
    'avl': 'a',
    'limit': '100',
    'page': 1
}
TELEGRAM_TOKEN =
TELEGRAM_CHAT_ID = "-1002660176895_7"
SEEN_FILE = "seen_listings.json"
PRICE_HISTORY_FILE = "price_history.json"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Failed to send Telegram message:", e)

def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return json.load(f)  # {id: price}
    except Exception:
        return {}

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f)

def load_price_history():
    try:
        with open(PRICE_HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def save_price_history(history):
    with open(PRICE_HISTORY_FILE, "w") as f:
        json.dump(history, f)

def update_price_history(history, car_id, price):
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    price = float(price) if price is not None else None
    if car_id not in history:
        history[car_id] = [[now, price]]
    else:
        # Only append if price changed
        if price != history[car_id][-1][1]:
            history[car_id].append([now, price])
    return history

def build_url(page):
    params = PARAMS.copy()
    params['page'] = page
    return BASE_URL + '?' + urlencode(params, doseq=True, quote_via=quote_plus)

def scrape_listings(page_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disk-cache-size=0")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-data-dir=C:\\Users\\cylbe\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.get(page_url)
    time.sleep(1)  # Wait for JS to render. Adjust as needed.
    driver.refresh()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    listings = []
    for div in soup.find_all("div", id=re.compile(r"^listing_\d+$")):
        try:
            model_tag = div.select_one(".styles_model_name__ZaHTI")
            model = model_tag.text.strip() if model_tag else "N/A"
            link_tag = div.select_one("a.styles_text_link__wBaHL")
            link = link_tag['href'] if link_tag and link_tag.has_attr('href') else ""
            if link and not link.startswith("http"):
                link = "https://www.sgcarmart.com" + link
            price_tag = div.select_one(".styles_price__PoUIK")
            price_text = price_tag.text.strip() if price_tag else "N/A"
            price_value = None
            if price_text != "N/A":
                price_value = float(price_text.replace('$', '').replace(',', '').strip())
            dep_tag = div.select_one(".listing_depreciation_box__mRuxZ .styles_detail_text__13VQe")
            depreciation = dep_tag.text.strip() if dep_tag else "N/A"
            reg_tag = div.select_one(".listing_reg_year_box__k0Se9 .styles_reg_date_text__g7iO_ p.mb-0")
            reg_date = reg_tag.text.strip() if reg_tag else "N/A"
            mileage_tag = div.select_one(".listing_mileage_box__XvLqW .styles_detail_text__13VQe")
            mileage = mileage_tag.text.strip() if mileage_tag else "N/A"
            owners_tag = div.select_one(".listing_owner_box__IChW7 .styles_detail_text__13VQe")
            owners = owners_tag.text.strip() if owners_tag else "N/A"
            desc_tag = div.select_one(".styles_description__eQ2EJ")
            description = desc_tag.text.strip() if desc_tag else ""
            posted_tag = div.select_one(".styles_posted_date__ObxTu")
            posted_date = posted_tag.text.strip() if posted_tag else "N/A"
            match = re.search(r'ID=(\d+)', link)
            unique_id = match.group(1) if match else link
            listings.append({
                "id": unique_id,
                "model": model,
                "link": link,
                "price_text": price_text,
                "price_value": price_value,
                "depreciation": depreciation,
                "reg_date": reg_date,
                "mileage": mileage,
                "owners": owners,
                "description": description,
                "posted_date": posted_date
            })
        except Exception as e:
            print("Error parsing listing:", e)
    return listings

def main():
    while True:
        print(f"Starting SGcarmart Scraper @ {datetime.now(timezone(timedelta(hours=8)))}")
        seen = load_seen()  # {id: price}
        new_seen = dict(seen)
        price_history = load_price_history()
        page = 1
        while True:
            page_url = build_url(page)
            print(f"Scraping page {page}")
            listings = scrape_listings(page_url)
            if not listings:
                print("No more listings found, ending pagination.")
                break
            for car in listings:
                car_id = car["id"]
                car_price = car["price_value"]
                # --- Price history tracking ---
                price_history = update_price_history(price_history, car_id, car_price)
                # --- Notification logic ---
                if car_id not in seen:
                    # New listing
                    message = (
                        f"<b>{car['model']}</b>\n"
                        f"Price: {car['price_text']}\n"
                        f"Listed Depreciation: {car['depreciation']}\n"
                        f"Reg Date: {car['reg_date']}\n"
                        f"Mileage: {car['mileage']}\n"
                        f"Owners: {car['owners']}\n"
                        f"Posted: {car['posted_date']}\n"
                        f"<a href=\"{car['link']}\">View Listing</a>\n"
                        f"{car['description']}"
                    )
                    print("New car found:", car['model'])
                    send_telegram_message(message)
                    new_seen[car_id] = car_price
                else:
                    # Existing listing, check price change
                    old_price = seen.get(car_id)
                    if car_price is not None and old_price is not None and car_price != old_price:
                        # --- Format price history for Telegram ---
                        history_entries = price_history.get(car_id, [])
                        history_str = "\n".join(
                            [f"{datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M')}: ${p:,.2f}" for ts, p in
                             history_entries]
                        ) if history_entries else "No history available."
                        message = (
                            f"<b>{car['model']}</b>\n"
                            f"Price changed from ${old_price:,.2f} to {car['price_text']}\n"
                            f"Listed Depreciation: {car['depreciation']}\n"
                            f"Reg Date: {car['reg_date']}\n"
                            f"Mileage: {car['mileage']}\n"
                            f"Owners: {car['owners']}\n"
                            f"Posted: {car['posted_date']}\n"
                            f"<a href=\"{car['link']}\">View Listing</a>\n"
                            f"{car['description']}\n\n"
                            f"<b>Price History:</b>\n{history_str}"
                        )
                        print(f"Price change detected for {car['model']}: {old_price} -> {car_price}")
                        send_telegram_message(message)
                        new_seen[car_id] = car_price
            page += 1
        save_seen(new_seen)
        save_price_history(price_history)
        print("Cycle Ended")
        time.sleep(random.randint(31,42)*random.randint(1,2))

if __name__ == "__main__":
    main()
