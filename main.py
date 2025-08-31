from flask import Flask, request, jsonify
import requests
import yaml

# Load config
with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

BASE_SYMBOL = config.get("CURRENCY_RATE_BASE_SYMBOL", "KRW")

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
        params = {"symbols": final_symbols}
    else:
        params = {}
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
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(debug=True, port=8080)