from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.7049.115 Safari/537.36")
options.add_argument("start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)
# driver.get("https://www.sgcarmart.com/used-cars/listing?dp2=11000&fr=2017&to=2018&cts%5B%5D=18&vts%5B%5D=12&vts%5B%5D=13&vts%5B%5D=9&vts%5B%5D=10&vts%5B%5D=11&vts%5B%5D=8&vts%5B%5D=7&vts%5B%5D=3&vts%5B%5D=2&fue=Petrol&opc%5B%5D=0&avl=a&limit=100")
driver.get("https://bot.sannysoft.com/")

try:
    # Wait for listings AND verify they remain visible
    WebDriverWait(driver, 20).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div[id^='listing_']"))
    )
    print(f"Stable listings found: {len(driver.find_elements(By.CSS_SELECTOR, 'div[id^=\"listing_\"]'))}")

    # Take screenshot for verification
    driver.save_screenshot('loaded_page.png')

except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
