import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json
import os
from datetime import datetime

# ---------------------------
# FIREBASE INIT
# ---------------------------

firebase_json = os.environ.get("FIREBASE_KEY")

firebase_dict = json.loads(firebase_json)

cred = credentials.Certificate(firebase_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rate-calculator-ff3b1-default-rtdb.firebaseio.com/'
})

# ---------------------------
# DUMMY METAL DATA
# Replace later with API
# ---------------------------

copper_usd = 9850
zinc_usd = 2820
nickel_usd = 19120
lead_usd = 2140

usd_inr = 83.5

# ---------------------------
# CONVERSION
# USD/Ton -> INR/KG
# ---------------------------

copper_inr = (copper_usd * usd_inr) / 1000
zinc_inr = (zinc_usd * usd_inr) / 1000
nickel_inr = (nickel_usd * usd_inr) / 1000
lead_inr = (lead_usd * usd_inr) / 1000

# ---------------------------
# DATA
# ---------------------------

data = {
    "copper": {
        "usd_per_ton": copper_usd,
        "inr_per_kg": round(copper_inr, 2),
        "updated_at": str(datetime.now())
    },

    "zinc": {
        "usd_per_ton": zinc_usd,
        "inr_per_kg": round(zinc_inr, 2),
        "updated_at": str(datetime.now())
    },

    "nickel": {
        "usd_per_ton": nickel_usd,
        "inr_per_kg": round(nickel_inr, 2),
        "updated_at": str(datetime.now())
    },

    "lead": {
        "usd_per_ton": lead_usd,
        "inr_per_kg": round(lead_inr, 2),
        "updated_at": str(datetime.now())
    }
}

# ---------------------------
# PUSH TO FIREBASE
# ---------------------------

ref = db.reference("/metal_rates")

ref.set(data)

print("Metal rates updated successfully")
