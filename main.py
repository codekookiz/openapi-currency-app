from flask import Flask, request, jsonify
import requests
import streamlit as st
import os

BASE_SYMBOL = st.secrets["CURRENCY_RATE_BASE_SYMBOL"]
API_KEY = st.secrets["CURRENCY_RATE_API_KEY"]

app = Flask(__name__)

API_URL = "https://api.exchangerate.host/latest"
SUPPORTED_URL = "https://api.exchangerate.host/symbols"

@app.route("/api/v1/currencyrate/now", methods=["GET"])
def get_rate_now():
    symbols = request.args.get("symbols")
    if symbols:
        symbol_set = set(symbols.split(","))
        symbol_set.add(BASE_SYMBOL)
        final_symbols = ",".join(symbol_set)
        params = {"symbols": final_symbols, "access_key": API_KEY}
    else:
        params = {"access_key": API_KEY}
    response = requests.get(API_URL, params=params)
    data = response.json()

    won = data["rates"].get("KRW")
    result = {
        "success": data.get("success"),
        "timestamp": data.get("timestamp"),
        "date": data.get("date"),
        "rates": {}
    }

    for curr, rate in data["rates"].items():
        if curr in ["KRW", "BTC"]:
            continue
        elif curr == "JPY":
            result["rates"][f"{curr} (100)"] = round(won / rate * 100, 2)
        else:
            result["rates"][curr] = round(won / rate, 2)

    return jsonify(result)

@app.route("/api/v1/currencyrate/supported", methods=["GET"])
def get_supported_currencies():
    response = requests.get(SUPPORTED_URL)
    return response.json()


st.title("Currency Rate API Service")

curr_list = get_supported_currencies()

st.table({
    "Currency" : curr_list.symbols.keys(),
    "Description" : curr_list.values()
})

if __name__ == "__main__":
    pass