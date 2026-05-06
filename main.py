import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import requests
import json
import os
from datetime import datetime

# ---------------------------------------------------
# FIREBASE INIT
# ---------------------------------------------------

firebase_json = os.environ.get("FIREBASE_KEY")

firebase_dict = json.loads(firebase_json)

cred = credentials.Certificate(firebase_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rate-calculator-ff3b1-default-rtdb.firebaseio.com/'
})

# ---------------------------------------------------
# LIVE USD INR
# ---------------------------------------------------

usd_inr = 83.5

# ---------------------------------------------------
# FREE LIVE METAL DATA
# ---------------------------------------------------

# Using static fallback + easy API architecture

metals = {

    "copper": 9800,
    "zinc": 2700,
    "nickel": 19000,
    "lead": 2100,
    "tin": 32000

}

# ---------------------------------------------------
# CALCULATE INR/KG
# ---------------------------------------------------

data = {}

for metal, usd_per_ton in metals.items():

    inr_per_kg = (usd_per_ton * usd_inr) / 1000

    data[metal] = {

        "usd_per_ton": usd_per_ton,

        "inr_per_kg": round(inr_per_kg, 2),

        "updated_at": str(datetime.now())
    }

# ---------------------------------------------------
# PUSH TO FIREBASE
# ---------------------------------------------------

ref = db.reference("/metal_rates")

ref.set(data)

print("Metal prices updated successfully")
