import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

from playwright.sync_api import sync_playwright

import json
import os
import re

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
# SETTINGS
# =====================================================

usd_inr = 83.5

metal_urls = {

    "copper": "https://www.investing.com/commodities/copper",

    "zinc": "https://www.investing.com/commodities/lme-zinc",

    "nickel": "https://www.investing.com/commodities/lme-nickel",

    "lead": "https://www.investing.com/commodities/lead",

    "tin": "https://www.investing.com/commodities/lme-tin"

}

firebase_data = {}

# =====================================================
# PLAYWRIGHT
# =====================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
    headless=True,
    args=["--no-sandbox"]
)
    page = browser.new_page()

    for metal, url in metal_urls.items():

        try:

            print("Fetching:", metal)

            page.goto(url, timeout=60000)

            page.wait_for_timeout(5000)

            html = page.content()

            # Find live price
            matches = re.findall(r'"last":"([\d,\.]+)"', html)

            if matches:

                value = matches[0].replace(",", "")

                usd_per_ton = float(value)

                inr_per_kg = (usd_per_ton * usd_inr) / 1000

                firebase_data[metal] = {

                    "usd_per_ton": round(usd_per_ton, 2),

                    "inr_per_kg": round(inr_per_kg, 2),

                    "updated_at": str(datetime.now())

                }

                print(metal, usd_per_ton)

            else:

                print("No value found:", metal)

        except Exception as e:

            print("Error:", metal, e)

    browser.close()

# =====================================================
# SAFE FIREBASE PUSH
# =====================================================

if len(firebase_data) > 0:

    ref = db.reference("/metal_rates")

    ref.set(firebase_data)

    print("Real live metals updated successfully")

else:

    print("No data found")
