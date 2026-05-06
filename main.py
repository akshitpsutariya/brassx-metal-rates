import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import requests
from bs4 import BeautifulSoup

import json
import os
import re

from datetime import datetime

# ===================================================
# FIREBASE INIT
# ===================================================

firebase_json = os.environ.get("FIREBASE_KEY")

firebase_dict = json.loads(firebase_json)

cred = credentials.Certificate(firebase_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rate-calculator-ff3b1-default-rtdb.firebaseio.com/'
})

# ===================================================
# USD INR RATE
# ===================================================

usd_inr = 83.5

# ===================================================
# FETCH TRADING ECONOMICS
# ===================================================

url = "https://tradingeconomics.com/commodities"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

html = response.text

# ===================================================
# PARSE HTML
# ===================================================

soup = BeautifulSoup(html, "html.parser")

tables = soup.find_all("table")

# ===================================================
# STORE METALS
# ===================================================

metals = {}

# ===================================================
# EXTRACT ROWS
# ===================================================

for table in tables:

    rows = table.find_all("tr")

    for row in rows:

        cols = row.find_all("td")

        if len(cols) > 1:

            try:

                name = cols[0].get_text(strip=True).lower()

                price_text = cols[1].get_text(strip=True)

                # Remove commas
                price_text = price_text.replace(",", "")

                # Extract number
                match = re.search(r"[\d\.]+", price_text)

                if match:

                    value = float(match.group())

                    if "copper" in name:
                        metals["copper"] = value

                    elif "zinc" in name:
                        metals["zinc"] = value

                    elif "nickel" in name:
                        metals["nickel"] = value

                    elif "lead" in name:
                        metals["lead"] = value

                    elif "tin" in name:
                        metals["tin"] = value

            except Exception as e:
                print("Row error:", e)

# ===================================================
# DEBUG PRINT
# ===================================================

print("Fetched Metals:", metals)

# ===================================================
# CREATE FIREBASE DATA
# ===================================================

data = {}

for metal, usd_per_ton in metals.items():

    inr_per_kg = (usd_per_ton * usd_inr) / 1000

    data[metal] = {

        "usd_per_ton": round(usd_per_ton, 2),

        "inr_per_kg": round(inr_per_kg, 2),

        "updated_at": str(datetime.now())

    }

# ===================================================
# PUSH TO FIREBASE
# ===================================================

ref = db.reference("/metal_rates")

ref.set(data)

print("Live metal prices updated successfully")
