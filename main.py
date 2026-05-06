import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
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
# USD INR
# ---------------------------------------------------

usd_inr = 83.5

# ---------------------------------------------------
# FETCH WEBSITE
# ---------------------------------------------------

url = "https://www.dailymetalprice.com/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

html = response.text

# ---------------------------------------------------
# PARSE HTML
# ---------------------------------------------------

soup = BeautifulSoup(html, "lxml")

tables = soup.find_all("table")

# ---------------------------------------------------
# DEFAULT VALUES
# ---------------------------------------------------

copper_usd_lb = 0
zinc_usd_lb = 0
nickel_usd_lb = 0
lead_usd_lb = 0

# ---------------------------------------------------
# SEARCH TABLE DATA
# ---------------------------------------------------

for table in tables:

    rows = table.find_all("tr")

    for row in rows:

        text = row.get_text(" ", strip=True).lower()

        try:

            if "copper" in text and copper_usd_lb == 0:

                value = text.split("$")[1].split("lb")[0]
                copper_usd_lb = float(value)

            if "zinc" in text and zinc_usd_lb == 0:

                value = text.split("$")[1].split("lb")[0]
                zinc_usd_lb = float(value)

            if "nickel" in text and nickel_usd_lb == 0:

                value = text.split("$")[1].split("lb")[0]
                nickel_usd_lb = float(value)

            if "lead" in text and lead_usd_lb == 0:

                value = text.split("$")[1].split("lb")[0]
                lead_usd_lb = float(value)

        except:
            pass

# ---------------------------------------------------
# CONVERT LB -> TON
# ---------------------------------------------------

LB_TO_TON = 2204.62

copper_usd_ton = copper_usd_lb * LB_TO_TON
zinc_usd_ton = zinc_usd_lb * LB_TO_TON
nickel_usd_ton = nickel_usd_lb * LB_TO_TON
lead_usd_ton = lead_usd_lb * LB_TO_TON

# ---------------------------------------------------
# INR/KG
# ---------------------------------------------------

copper_inr = (copper_usd_ton * usd_inr) / 1000
zinc_inr = (zinc_usd_ton * usd_inr) / 1000
nickel_inr = (nickel_usd_ton * usd_inr) / 1000
lead_inr = (lead_usd_ton * usd_inr) / 1000

# ---------------------------------------------------
# DATA
# ---------------------------------------------------

data = {

    "copper": {
        "usd_per_ton": round(copper_usd_ton, 2),
        "inr_per_kg": round(copper_inr, 2),
        "updated_at": str(datetime.now())
    },

    "zinc": {
        "usd_per_ton": round(zinc_usd_ton, 2),
        "inr_per_kg": round(zinc_inr, 2),
        "updated_at": str(datetime.now())
    },

    "nickel": {
        "usd_per_ton": round(nickel_usd_ton, 2),
        "inr_per_kg": round(nickel_inr, 2),
        "updated_at": str(datetime.now())
    },

    "lead": {
        "usd_per_ton": round(lead_usd_ton, 2),
        "inr_per_kg": round(lead_inr, 2),
        "updated_at": str(datetime.now())
    }
}

# ---------------------------------------------------
# PUSH TO FIREBASE
# ---------------------------------------------------

ref = db.reference("/metal_rates")

ref.set(data)

print("Live metal prices updated successfully")
