from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth


options = Options()
options.add_argument("start-maximized")

# Chrome is controlled by automated test software
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
# s = Service('C:\\BrowserDrivers\\chromedriver.exe')
driver = webdriver.Chrome(options=options)

# Selenium Stealth settings
stealth(driver,
      languages=["en-US", "en"],
      vendor="Google Inc.",
      platform="Win32",
      webgl_vendor="Intel Inc.",
      renderer="Intel Iris OpenGL Engine",
      fix_hairline=True,
  )

# driver.get("https://bot.sannysoft.com/")
driver.get("https://www.sgcarmart.com/used-cars/listing?dp2=11000&fr=2017&to=2018&cts%5B%5D=18&vts%5B%5D=12&vts%5B%5D=13&vts%5B%5D=9&vts%5B%5D=10&vts%5B%5D=11&vts%5B%5D=8&vts%5B%5D=7&vts%5B%5D=3&vts%5B%5D=2&fue=Petrol&opc%5B%5D=0&avl=a&limit=100")
