import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import requests
from bs4 import BeautifulSoup

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
# USD INR
# =====================================================

usd_inr = 83.5

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

# =====================================================
# HEADERS
# =====================================================

headers = {
    "User-Agent": "Mozilla/5.0"
}

# =====================================================
# FETCH FUNCTION
# =====================================================

def fetch_price(url):

    try:

        response = requests.get(url, headers=headers)

        html = response.text

        # regex for live price
        matches = re.findall(r'"last":"([\d,\.]+)"', html)

        if matches:

            value = matches[0].replace(",", "")

            return float(value)

        # fallback parser
        soup = BeautifulSoup(html, "html.parser")

        text = soup.get_text(" ", strip=True)

        number_match = re.search(r'([\d,]+\.\d+)', text)

        if number_match:

            value = number_match.group(1).replace(",", "")

            return float(value)

        return None

    except Exception as e:

        print("Error:", e)

        return None

# =====================================================
# FETCH METALS
# =====================================================

firebase_data = {}

for metal, url in metal_urls.items():

    print("Fetching:", metal)

    price = fetch_price(url)

    print("Price:", price)

    if price:

        usd_per_ton = price

        inr_per_kg = (usd_per_ton * usd_inr) / 1000

        firebase_data[metal] = {

            "usd_per_ton": round(usd_per_ton, 2),

            "inr_per_kg": round(inr_per_kg, 2),

            "updated_at": str(datetime.now())

        }

# =====================================================
# SAFE PUSH
# =====================================================

if len(firebase_data) > 0:

    ref = db.reference("/metal_rates")

    ref.set(firebase_data)

    print("Live metals updated successfully")

else:

    print("No data found. Firebase not updated.")
