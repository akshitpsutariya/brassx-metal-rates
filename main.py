import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import requests
import json
import os
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
# SETTINGS
# ===================================================

API_KEY = "VjyaYTkTRfLKs4ljhiYNvNYdhhBwOnO5"

usd_inr = 83.5

# ===================================================
# METAL SYMBOLS
# ===================================================

symbols = {

    "copper": "HGUSD",
    "zinc": "ZNCUSD",
    "nickel": "NICKELUSD",
    "lead": "LEADUSD",
    "tin": "TINUSD"

}

data = {}

# ===================================================
# FETCH LIVE METAL DATA
# ===================================================

for metal, symbol in symbols.items():

    try:

        url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={API_KEY}"

        response = requests.get(url)

        result = response.json()

        print(f"{metal} response:", result)

        if isinstance(result, list) and len(result) > 0:

            usd_per_ton = float(result[0]["price"])

        else:

            usd_per_ton = 0

        # USD/TON -> INR/KG

        inr_per_kg = (usd_per_ton * usd_inr) / 1000

        data[metal] = {

            "usd_per_ton": round(usd_per_ton, 2),

            "inr_per_kg": round(inr_per_kg, 2),

            "updated_at": str(datetime.now())

        }

    except Exception as e:

        data[metal] = {

            "error": str(e),

            "updated_at": str(datetime.now())

        }

# ===================================================
# PUSH TO FIREBASE
# ===================================================

ref = db.reference("/metal_rates")

ref.set(data)

print("Live metal prices updated successfully")
