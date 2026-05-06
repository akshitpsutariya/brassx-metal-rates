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
# USD INR
# =====================================================

usd_inr = float(
    yf.Ticker("USDINR=X")
    .history(period="1d")["Close"]
    .iloc[-1]
)

# =====================================================
# REAL YAHOO METAL SYMBOLS
# =====================================================

symbols = {

    "copper": "HG=F",
    "nickel": "NI=F",
    "zinc": "ZN=F",
    "lead": "PB=F",
    "tin": "SN=F"

}

firebase_data = {}

# =====================================================
# FETCH LIVE DATA
# =====================================================

for metal, symbol in symbols.items():

    try:

        ticker = yf.Ticker(symbol)

        hist = ticker.history(period="1d")

        if not hist.empty:

            price = float(hist["Close"].iloc[-1])

            firebase_data[metal] = {

                "usd_price": round(price, 2),

                "inr_estimated": round(price * usd_inr, 2),

                "updated_at": str(datetime.now())

            }

            print(metal, price)

        else:

            print("No data:", metal)

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
