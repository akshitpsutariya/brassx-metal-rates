import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import json
import os
import time
from datetime import datetime

# =====================================================
# FIREBASE INIT
# =====================================================

firebase_json = os.environ.get("FIREBASE_KEY")

firebase_dict = json.loads(firebase_json)

cred = credentials.Certificate(firebase_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rate-calculator-ff3b1-default-rtdb.firebaseio.com/'
})

# =====================================================
# CHROME OPTIONS
# =====================================================

options = Options()

options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# =====================================================
# METAL URLS
# =====================================================

metal_urls = {

    "copper": "https://www.investing.com/commodities/copper",

    "zinc": "https://www.investing.com/commodities/lme-zinc",

    "nickel": "https://www.investing.com/commodities/lme-nickel",

    "lead": "https://www.investing.com/commodities/lead",

    "tin": "https://www.investing.com/commodities/lme-tin"

}

usd_inr = 83.5

firebase_data = {}

# =====================================================
# FETCH LIVE VALUES
# =====================================================

for metal, url in metal_urls.items():

    try:

        print("Fetching:", metal)

        driver.get(url)

        time.sleep(6)

        selectors = [

            '[data-test="instrument-price-last"]',

            'div[data-test="instrument-price-last"]',

            'span[data-test="instrument-price-last"]'

        ]

        price = None

        for selector in selectors:

            try:

                element = driver.find_element(By.CSS_SELECTOR, selector)

                text = element.text.replace(",", "")

                price = float(text)

                break

            except:
                pass

        if price:

            inr_per_kg = (price * usd_inr) / 1000

            firebase_data[metal] = {

                "usd_per_ton": round(price, 2),

                "inr_per_kg": round(inr_per_kg, 2),

                "updated_at": str(datetime.now())

            }

            print(metal, price)

        else:

            print("Price not found:", metal)

    except Exception as e:

        print("Error:", metal, str(e))

# =====================================================
# CLOSE DRIVER
# =====================================================

driver.quit()

# =====================================================
# SAFE PUSH
# =====================================================

if len(firebase_data) > 0:

    ref = db.reference("/metal_rates")

    ref.set(firebase_data)

    print("REAL live metals updated")

else:

    print("No metal data fetched")
