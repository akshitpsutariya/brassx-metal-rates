import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import json
import os
import requests
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
# SIMPLE WORKING METAL DATA
# =====================================================

metals = {

    "copper": 9800,
    "zinc": 2650,
    "nickel": 19100,
    "lead": 1980,
    "tin": 32500

}

usd_inr = 83.5

firebase_data = {}

# =====================================================
# CREATE DATA
# =====================================================

for metal, usd_per_ton in metals.items():

    inr_per_kg = (usd_per_ton * usd_inr) / 1000

    firebase_data[metal] = {

        "usd_per_ton": round(usd_per_ton, 2),

        "inr_per_kg": round(inr_per_kg, 2),

        "updated_at": str(datetime.now())

    }

# =====================================================
# PUSH TO FIREBASE
# =====================================================

ref = db.reference("/metal_rates")

ref.set(firebase_data)

print("SUCCESS: Metal prices updated")
