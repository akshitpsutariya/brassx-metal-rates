import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import yfinance as yf

import json
import os
from datetime import datetime

# ------------------------------------------------
# FIREBASE INIT
# ------------------------------------------------

firebase_json = os.environ.get("FIREBASE_KEY")

firebase_dict = json.loads(firebase_json)

cred = credentials.Certificate(firebase_dict)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://rate-calculator-ff3b1-default-rtdb.firebaseio.com/'
})

# ------------------------------------------------
# LIVE USD INR
# ------------------------------------------------

usd_inr = yf.Ticker("USDINR=X").history(period="1d")['Close'].iloc[-1]

# ------------------------------------------------
# LIVE COPPER PRICE
# Yahoo Finance Copper Futures
# HG=F
# Price is USD per pound
# ------------------------------------------------

copper_price_per_pound = yf.Ticker("HG=F").history(period="1d")['Close'].iloc[-1]

# ------------------------------------------------
# CONVERT COPPER
# Pound → Ton
# ------------------------------------------------

copper_usd_ton = copper_price_per_pound * 2204.62

# ------------------------------------------------
# TEMPORARY VALUES
# Until live sources added
# ------------------------------------------------

zinc_usd_ton = 2820
nickel_usd_ton = 19120
lead_usd_ton = 2140

# ------------------------------------------------
# USD/TON → INR/KG
# ------------------------------------------------

copper_inr_kg = (copper_usd_ton * usd_inr) / 1000
zinc_inr_kg = (zinc_usd_ton * usd_inr) / 1000
nickel_inr_kg = (nickel_usd_ton * usd_inr) / 1000
lead_inr_kg = (lead_usd_ton * usd_inr) / 1000

# ------------------------------------------------
# FINAL DATA
# ------------------------------------------------

data = {

    "copper": {
        "usd_per_ton": round(copper_usd_ton, 2),
        "inr_per_kg": round(copper_inr_kg, 2),
        "updated_at": str(datetime.now())
    },

    "zinc": {
        "usd_per_ton": zinc_usd_ton,
        "inr_per_kg": round(zinc_inr_kg, 2),
        "updated_at": str(datetime.now())
    },

    "nickel": {
        "usd_per_ton": nickel_usd_ton,
        "inr_per_kg": round(nickel_inr_kg, 2),
        "updated_at": str(datetime.now())
    },

    "lead": {
        "usd_per_ton": lead_usd_ton,
        "inr_per_kg": round(lead_inr_kg, 2),
        "updated_at": str(datetime.now())
    }
}

# ------------------------------------------------
# PUSH TO FIREBASE
# ------------------------------------------------

ref = db.reference("/metal_rates")

ref.set(data)

print("Live metal prices updated successfully")
