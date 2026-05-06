import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import requests
import json
import os

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
# INVESTING IDS
# =====================================================

metals = {

    "copper": "8830",
    "zinc": "8832",
    "nickel": "8831",
    "lead": "8833",
    "tin": "49789"

}

# =====================================================
# HEADERS
# =====================================================

headers = {

    "User-Agent": "Mozilla/5.0",

    "X-Requested-With": "XMLHttpRequest"

}

# =====================================================
# FETCH FUNCTION
# =====================================================

def fetch_price(pair_id):

    try:

        url = f"https://api.investing.com/api/financialdata/{pair_id}/historical/chart/?period=PT1H"

        response = requests.get(url, headers=headers)

        result = response.json()

        data = result.get("data", [])

        if len(data) > 0:

            latest = data[-1]

            price = latest.get("last_close", None)

            return float(price)

        return None

    except Exception as e:

        print("Error:", e)

        return None

# =====================================================
# CREATE DATA
# =====================================================

firebase_data = {}

for metal, pair_id in metals.items():

    print("Fetching:", metal)

    price = fetch_price(pair_id)

    print("Price:", price)

    if price:

        usd_per_ton = price

        inr_per_kg = (usd_per_ton * usd_inr) / 1000

        firebase_data[metal] = {

            "usd_per_ton": round(usd_per_ton, 2),

            "inr_per_kg": round(inr_per_kg, 2),

            "updated_at": str(datetime.now())

        }

    else:

        firebase_data[metal] = {

            "error": "Price not found",

            "updated_at": str(datetime.now())

        }

# =====================================================
# PUSH TO FIREBASE
# =====================================================

ref = db.reference("/metal_rates")

ref.set(firebase_data)

print("Live metals updated successfully")
