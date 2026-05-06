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
# SETTINGS
# =====================================================

API_KEY = "VjyaYTkTRfLKs4ljhiYNvNYdhhBwOnO5"

usd_inr = 83.5

# =====================================================
# REAL COMMODITY SYMBOLS
# =====================================================

symbols = {

    "copper": "HGUSD",
    "nickel": "NICKEL",
    "lead": "LEAD",
    "zinc": "ZINC",
    "tin": "TIN"

}

firebase_data = {}

# =====================================================
# FETCH
# =====================================================

for metal, symbol in symbols.items():

    try:

        url = f"https://financialmodelingprep.com/api/v3/quote-short/{symbol}?apikey={API_KEY}"

        response = requests.get(url)

        result = response.json()

        print(metal, result)

        if isinstance(result, list) and len(result) > 0:

            price = float(result[0]["price"])

            inr_per_kg = (price * usd_inr) / 1000

            firebase_data[metal] = {

                "usd_per_ton": round(price, 2),

                "inr_per_kg": round(inr_per_kg, 2),

                "updated_at": str(datetime.now())

            }

    except Exception as e:

        print("ERROR:", metal, str(e))

# =====================================================
# PUSH
# =====================================================

if len(firebase_data) > 0:

    ref = db.reference("/metal_rates")

    ref.set(firebase_data)

    print("SUCCESS")

else:

    print("NO DATA")
