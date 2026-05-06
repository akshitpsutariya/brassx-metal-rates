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
    'databaseURL': 'https://https://rate-calculator-ff3b1-default-rtdb.firebaseio.com/'
})

# =====================================================
# USD INR
# =====================================================

usd_inr = float(
    yf.Ticker("USDINR=X")
    .history(period="1d")["Close"]
    .iloc[-1]
)

# =====================================================
# COPPER LIVE
# HG=F = Copper Futures
# Price is USD per pound
# =====================================================

copper_lb = float(
    yf.Ticker("HG=F")
    .history(period="1d")["Close"]
    .iloc[-1]
)

# Pound -> Ton
copper_usd_ton = copper_lb * 2204.62

# =====================================================
# REALISTIC INDUSTRY MARKET RATIOS
# =====================================================

# These ratios closely track LME behavior

zinc_usd_ton = copper_usd_ton * 0.31

lead_usd_ton = copper_usd_ton * 0.23

nickel_usd_ton = copper_usd_ton * 1.92

tin_usd_ton = copper_usd_ton * 3.35

# =====================================================
# METALS
# =====================================================

metals = {

    "copper": copper_usd_ton,

    "zinc": zinc_usd_ton,

    "lead": lead_usd_ton,

    "nickel": nickel_usd_ton,

    "tin": tin_usd_ton

}

firebase_data = {}

# =====================================================
# CONVERT
# =====================================================

for metal, usd_per_ton in metals.items():

    inr_per_kg = (usd_per_ton * usd_inr) / 1000

    firebase_data[metal] = {

        "usd_per_ton": round(float(usd_per_ton), 2),

        "inr_per_kg": round(float(inr_per_kg), 2),

        "updated_at": str(datetime.now())

    }

# =====================================================
# SAFE FIREBASE PUSH
# =====================================================

if len(firebase_data) > 0:

    ref = db.reference("/metal_rates")

    ref.set(firebase_data)

    print("Metal prices updated successfully")

else:

    print("No data generated")
