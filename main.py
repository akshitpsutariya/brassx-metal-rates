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
# REAL METAL DATA
# =====================================================

metal_urls = {

    "copper": "https://api.tradingeconomics.com/commodities/copper",

    "zinc": "https://api.tradingeconomics.com/commodities/zinc",

    "nickel": "https://api.tradingeconomics.com/commodities/nickel",

    "lead": "https://api.tradingeconomics.com/commodities/lead",

    "tin": "https://api.tradingeconomics.com/commodities/tin"

}

firebase_data = {}

# =====================================================
# FETCH FUNCTION
# =====================================================

for metal, url in metal_urls.items():

    try:

        response = requests.get(url)

        text = response.text

        # Extract numeric values
        import re

        matches = re.findall(r'"LastPrice":([\d\.]+)', text)

        if matches:

            usd_per_ton = float(matches[0])

            inr_per_kg = (usd_per_ton * usd_inr) / 1000

            firebase_data[metal] = {

                "usd_per_ton": round(usd_per_ton, 2),

                "inr_per_kg": round(inr_per_kg, 2),

                "updated_at": str(datetime.now())

            }

            print(metal, usd_per_ton)

        else:

            print("No price:", metal)

    except Exception as e:

        print("Error:", metal, e)

# =====================================================
# SAFE FIREBASE PUSH
# =====================================================

if len(firebase_data) > 0:

    ref = db.reference("/metal_rates")

    ref.set(firebase_data)

    print("Live metals updated successfully")

else:

    print("No data fetched")
