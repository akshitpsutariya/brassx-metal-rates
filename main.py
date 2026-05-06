import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import requests
from bs4 import BeautifulSoup

import json
import os
import re

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

usd_inr = 83.5

url = "https://in.investing.com/commodities/metals"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# =====================================================
# FETCH PAGE
# =====================================================

response = requests.get(url, headers=headers)

html = response.text

# =====================================================
# PARSE HTML
# =====================================================

soup = BeautifulSoup(html, "html.parser")

text = soup.get_text("\n", strip=True)

lines = text.split("\n")

# =====================================================
# METALS
# =====================================================

metals = {}

# =====================================================
# EXTRACT VALUES
# =====================================================

for i, line in enumerate(lines):

    line_lower = line.lower()

    try:

        # COPPER
        if "copper derived" in line_lower:

            for j in range(i, i + 5):

                value_line = lines[j].replace(",", "")

                match = re.search(r"\d+\.\d+|\d+", value_line)

                if match:

                    metals["copper"] = float(match.group())
                    break

        # ZINC
        elif "zinc derived" in line_lower:

            for j in range(i, i + 5):

                value_line = lines[j].replace(",", "")

                match = re.search(r"\d+\.\d+|\d+", value_line)

                if match:

                    metals["zinc"] = float(match.group())
                    break

        # NICKEL
        elif "nickel derived" in line_lower:

            for j in range(i, i + 5):

                value_line = lines[j].replace(",", "")

                match = re.search(r"\d+\.\d+|\d+", value_line)

                if match:

                    metals["nickel"] = float(match.group())
                    break

        # LEAD
        elif "lead derived" in line_lower:

            for j in range(i, i + 5):

                value_line = lines[j].replace(",", "")

                match = re.search(r"\d+\.\d+|\d+", value_line)

                if match:

                    metals["lead"] = float(match.group())
                    break

        # TIN
        elif line_lower.strip() == "tin":

            for j in range(i, i + 5):

                value_line = lines[j].replace(",", "")

                match = re.search(r"\d+\.\d+|\d+", value_line)

                if match:

                    metals["tin"] = float(match.group())
                    break

    except Exception as e:

        print("Error:", e)

# =====================================================
# DEBUG
# =====================================================

print("Fetched Metals:", metals)

# =====================================================
# CREATE FIREBASE DATA
# =====================================================

firebase_data = {}

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

print("Live metals updated successfully")
