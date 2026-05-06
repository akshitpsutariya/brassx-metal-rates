import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import yfinance as yf

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
# LIVE USD INR
# =====================================================

usd_inr = yf.Ticker("USDINR=X").history(period="1d")["Close"].iloc[-1]

# =====================================================
# LIVE COPPER
# HG=F = Copper Futures
# USD per pound
# =====================================================

copper_lb = yf.Ticker("HG=F").history(period="1d")["Close"].iloc[-1]

# LB -> TON
copper_usd_ton = copper_lb * 2204.62

# =====================================================
# INDUSTRY ESTIMATED LIVE METALS
# Derived from copper movement
# =====================================================

zinc_usd_ton = copper_usd_ton * 0.28

lead_usd_ton = copper_usd_ton * 0.22

nickel_usd_ton = copper_usd_ton * 1.95

tin_usd_ton = copper_usd_ton * 3.2

# =====================================================
# INR/KG
# =====================================================

metals = {

    "copper": copper_usd_ton,
    "zinc": zinc_usd_ton,
    "lead": lead_usd_ton,
    "nickel": nickel_usd_ton,
    "tin": tin_usd_ton

}

firebase_data = {}

for metal, usd_per_ton in metals.items():

    inr_per_kg = (usd_per_ton * usd_inr) / 1000

    firebase_data[metal] = {

        "usd_per_ton": round(float(usd_per_ton), 2),

        "inr_per_kg": round(float(inr_per_kg), 2),

        "updated_at": str(datetime.now())

    }

# =====================================================
# PUSH TO FIREBASE
# =====================================================

if len(firebase_data) > 0:

    ref = db.reference("/metal_rates")

    ref.set(firebase_data)

    print("Metal prices updated successfully")

else:

    print("No data found")
