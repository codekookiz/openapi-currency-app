from flask import Flask, request, jsonify
import requests
import streamlit as st
import pandas as pd

API_KEY = st.secrets["CURRENCY_RATE_API_KEY"]

app = Flask(__name__)

API_URL = "https://api.exchangeratesapi.io/latest"
SUPPORTED_URL = "https://api.exchangeratesapi.io/symbols"

@app.route("/api/v1/currencyrate/supported", methods=["GET"])
def get_supported_currencies():
    response = requests.get(SUPPORTED_URL, params={"access_key": API_KEY})
    return response.json()

def get_rate_now(symbols):
    if symbols:
        symbol_set = set(symbols.split(","))
        symbol_set.add(BASE_SYMBOL)
        final_symbols = ",".join(symbol_set)
        params = {"base": "EUR", "symbols": final_symbols, "access_key": API_KEY}
    else:
        params = {"access_key": API_KEY}
    response = requests.get(API_URL, params=params)
    data = response.json()

    if not data.get("success", False) or "rates" not in data:
        return {
            "success": False,
            "error": data.get("error", {"message": "Unknown error occurred"}),
            "rates": {}
        }

    currcurr = data["rates"].get(BASE_SYMBOL)
    result = {
        "success": data.get("success"),
        "timestamp": data.get("timestamp"),
        "date": data.get("date"),
        "rates": {}
    }

    for curr, rate in data["rates"].items():
        if curr in [BASE_SYMBOL, "BTC"]:
            continue
        else:
            result["rates"][f"{curr} {BASE_AMOUNT_1}"] = f"{BASE_SYMBOL} {round(currcurr / rate * BASE_AMOUNT_1, 4)}"

    return result

def get_rate(symbols):
    if symbols:
        symbol_set = set(symbols.split(","))
        symbol_set.add(BASE_SYMBOL_AMOUNT)
        final_symbols = ",".join(symbol_set)
        params = {"base": "EUR", "symbols": final_symbols, "access_key": API_KEY}
    else:
        params = {"access_key": API_KEY}
    response = requests.get(API_URL, params=params)
    data = response.json()

    if not data.get("success", False) or "rates" not in data:
        return {
            "success": False,
            "error": data.get("error", {"message": "Unknown error occurred"}),
            "rates": {}
        }

    currcurr = data["rates"].get(BASE_SYMBOL_AMOUNT)
    result = {
        "success": data.get("success"),
        "timestamp": data.get("timestamp"),
        "date": data.get("date"),
        "rates": {}
    }

    for curr, rate in data["rates"].items():
        if curr in [BASE_SYMBOL_AMOUNT, "BTC"]:
            continue
        else:
            result["rates"][curr] = round(rate / currcurr * BASE_AMOUNT_2, 4)

    return result


st.title("Currency Rate API Service")

curr_list = get_supported_currencies()
total_list = {}
for k in curr_list["symbols"].keys():
    if k == "BTC":
        continue
    else:
        total_list[k] = curr_list["symbols"][k]

df1 = pd.DataFrame({
    "Currency": list(total_list.keys()),
    "Description": list(total_list.values())
}).reset_index(drop=True)

st.dataframe(
    df1.style.set_properties(**{'text-align': 'center'}), 
    use_container_width=True,
    hide_index=True
)

st.write("----")

st.header("How much do I need to exchange?")
BASE_SYMBOL = st.selectbox("Select Base Currency", options=total_list.keys(), index=0, key="base_currency")
symbols_list = list(total_list.keys())
col1, col2 = st.columns([0.5, 1])
with col1:
    BASE_AMOUNT_1 = st.number_input("Select Currency Amount", min_value=1, value=1, step=1, key="base_amount")
with col2:
    selected_symbols = st.multiselect("Choose Target Currencies", options=symbols_list, key="multi_currency")

if st.button("Get Rates", key="get_rate"):
    symbols_input = selected_symbols[0] if len(selected_symbols) == 1 else ",".join(selected_symbols)
    rates = get_rate_now(symbols_input)
    df2 = pd.DataFrame({
        "Currency": list(map(str, rates["rates"].keys())),
        f"Rate": list(rates["rates"].values())
    }).reset_index(drop=True)

    st.dataframe(
        df2.style.set_properties(**{'text-align': 'center'}),
        use_container_width=True,
        hide_index=True
    )


st.write("----")

st.header("How much will I get if I exchange?")

col1, col2 = st.columns([1, 1])
with col1:
    BASE_AMOUNT_2 = st.number_input("Select Currency Amount", min_value=1, value=1, step=1, key="base_amount_amount")
with col2:
    BASE_SYMBOL_AMOUNT = st.selectbox("Select Base Currency", options=total_list.keys(), index=0, key="base_currency_amount")

symbols_list_amount = list(total_list.keys())
selected_symbols_amount = st.multiselect("Choose currencies", options=symbols_list_amount, key="multi_currency_amount")



if st.button("Get Rates", key="get_rate_amount"):
    symbols_input_amount = selected_symbols_amount[0] if len(selected_symbols_amount) == 1 else ",".join(selected_symbols_amount)
    rates = get_rate(symbols_input_amount)
    df2 = pd.DataFrame({
        "Currency": list(map(str, rates["rates"].keys())),
        f"Rate": list(rates["rates"].values())
    }).reset_index(drop=True)

    st.dataframe(
        df2.style.set_properties(**{'text-align': 'center'}),
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    pass