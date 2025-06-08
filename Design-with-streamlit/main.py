import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Cryptocurrency Dashboard", layout="wide")
st.title("Cryptocurrency Dashboard")
st.caption("Powered by CoinGecko API")

st.sidebar.header("Display Options")

# Sidebar widgets
num_coins = st.sidebar.slider("Number of coins to display", min_value=5, max_value=20, value=10)
show_market_cap = st.sidebar.checkbox("Show Market Cap Column", value=True)
refresh = st.sidebar.button("Refresh Data")

@st.cache_data
def get_top_cryptos(per_page):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    else:
        return pd.DataFrame()

df = get_top_cryptos(num_coins)

if df.empty:
    st.error("Failed to fetch cryptocurrency data. Please try again later.")
else:
    st.success("Live data loaded successfully.")

    st.subheader("Current Market Overview")
    columns_to_show = ["name", "symbol", "current_price", "price_change_percentage_24h"]
    if show_market_cap:
        columns_to_show.append("market_cap")
    st.dataframe(df[columns_to_show], use_container_width=True)

    st.header("7-Day Price Trend")

    coin_options = df["id"].tolist()
    selected_coin = st.selectbox("Select a cryptocurrency:", coin_options)

    def fetch_price_data(coin_id):
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": 7
        }
        res = requests.get(url, params=params)
        if res.status_code == 200:
            prices = res.json().get("prices", [])
            df_prices = pd.DataFrame(prices, columns=["Timestamp", "Price"])
            df_prices["Timestamp"] = pd.to_datetime(df_prices["Timestamp"], unit="ms")
            df_prices.set_index("Timestamp", inplace=True)
            return df_prices
        else:
            return None

    price_df = fetch_price_data(selected_coin)
    if price_df is not None:
        st.line_chart(price_df["Price"])
    else:
        st.warning("Could not load price data for the selected coin.")
