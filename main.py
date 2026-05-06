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
# USD -> INR
# =====================================================

usd_inr = 83.5

# =====================================================
# INVESTING.COM URLS
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

        soup = BeautifulSoup(html, "html.parser")

        # Try modern investing.com structure
        selectors = [

            'div[data-test="instrument-price-last"]',

            'span[data-test="instrument-price-last"]',

            'div.text-5xl',

            'span.text-2xl'

        ]

        for selector in selectors:

            tag = soup.select_one(selector)

            if tag:

                text = tag.get_text(strip=True)

                text = text.replace(",", "")

                match = re.search(r"[\d\.]+", text)

                if match:

                    return float(match.group())

        # fallback regex scan
        text = soup.get_text(" ", strip=True)

        match = re.search(r'last price[\s:]*([\d,\.]+)', text, re.IGNORECASE)

        if match:

            value = match.group(1).replace(",", "")

            return float(value)

        return None

    except Exception as e:

        print("Fetch error:", e)

        return None

# =====================================================
# FETCH ALL METALS
# =====================================================

data = {}

for metal, url in metal_urls.items():

    print(f"Fetching {metal}")

    price = fetch_price(url)

    print(f"{metal} price:", price)

    if price is not None:

        # Most investing values are already USD/TON
        usd_per_ton = price

        inr_per_kg = (usd_per_ton * usd_inr) / 1000

        data[metal] = {

            "usd_per_ton": round(usd_per_ton, 2),

            "inr_per_kg": round(inr_per_kg, 2),

            "updated_at": str(datetime.now())

        }

    else:

        data[metal] = {

            "error": "Price not found",

            "updated_at": str(datetime.now())

        }

# =====================================================
# PUSH TO FIREBASE
# =====================================================

ref = db.reference("/metal_rates")

ref.set(data)

print("Investing.com live metals updated successfully")
