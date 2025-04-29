
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
import ta

COINGECKO_API_BASE = "https://pro-api.coingecko.com/api/v3"
TOP_N_COINS = 300
HEADERS = {"x-cg-pro-api-key": st.secrets["general"]["COINGECKO_API_KEY"]}

def get_top_gainers(period="1h"):
    url = f"{COINGECKO_API_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": TOP_N_COINS,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_ohlc_data_light(coin_id, vs_currency="usd", days="1"):
    url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs_currency, "days": days}
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except:
        return []

def get_ohlc_data_full(coin_id, vs_currency="usd", days="1"):
    url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        prices = response.json().get("prices", [])
        return [[entry[0], entry[1], entry[1], entry[1], entry[1]] for entry in prices]
    except:
        return []

def get_btc_market_sentiment():
    url = f"{COINGECKO_API_BASE}/coins/bitcoin"
    params = {
        "localization": "false",
        "tickers": "false",
        "market_data": "true",
        "community_data": "false",
        "developer_data": "false",
        "sparkline": "false"
    }
    response = requests.get(url, params=params, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return data['market_data']['price_change_percentage_1h_in_currency']['usd']

def generate_paragraph(coin_name, rsi, gain):
    templates = [
        f"{coin_name} is showing strong bullish momentum with an RSI of {rsi:.1f}. It's gained {gain:.2f}% recently, suggesting ongoing buyer interest.",
        f"{coin_name} continues to push upward with an RSI reading of {rsi:.1f} and a recent gain of {gain:.2f}%. Momentum remains positive.",
        f"{coin_name} gained {gain:.2f}% and is tracking a rising RSI at {rsi:.1f}, suggesting strength in current price action.",
        f"Technical momentum is strong for {coin_name}, with RSI at {rsi:.1f} and price rising {gain:.2f}%. Bullish pressure appears sustainable."
    ]
    return random.choice(templates)

st.set_page_config(page_title="Crypto Dashboard v4.5.2", layout="wide")
st.title("🚀 Crypto Signal Dashboard v4.5.2 – Equal Cards + Indicator Breakdown")
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=120000, key="market_sentiment_refresh")

with st.sidebar:
    scan_mode = st.radio("Scanning Mode:", ("🛩️ Light Scan (1h)", "🧠 Full Scan (4h)"))
    gainer_period = st.radio("Top Gainers Period:", ("1h", "24h", "7d"))

btc_change = get_btc_market_sentiment()
btc_change_clamped = max(-5.0, min(5.0, btc_change))
gauge_value = (btc_change_clamped + 5) * (100 / 10)
fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=gauge_value,
    number={'suffix': "%"},
    gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "black", 'thickness': 0.3},
           'steps': [{'range': [0, 33], 'color': "red"},
                     {'range': [33, 66], 'color': "yellow"},
                     {'range': [66, 100], 'color': "green"}]},
    title={'text': "Market Sentiment (BTC 1h % Change)"}
))
st.plotly_chart(fig, use_container_width=True)

coins = get_top_gainers(period=gainer_period)
buy_signals = []

for coin in coins:
    coin_id = coin["id"]
    coin_name = coin["name"]
    coin_symbol = coin["symbol"].upper()
    coin_logo = coin["image"]
    price_change = coin.get(f"price_change_percentage_{gainer_period}_in_currency", 0)

    ohlc_data = get_ohlc_data_light(coin_id) if "Light" in scan_mode else get_ohlc_data_full(coin_id)
    if not ohlc_data:
        continue

    df = pd.DataFrame(ohlc_data, columns=["timestamp", "open", "high", "low", "close"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
    df.set_index('timestamp', inplace=True)

    if len(df) < 15:
        continue

    rsi_series = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    latest_rsi = rsi_series.dropna().iloc[-1] if not rsi_series.dropna().empty else None

    if latest_rsi is None or latest_rsi < 70:
        continue

    score = max(0, min(100, (70 - latest_rsi) * (100 / 40)))
    paragraph = generate_paragraph(coin_name, latest_rsi, price_change)
    buy_signals.append((coin_name, coin_symbol, coin_logo, score, latest_rsi, price_change, paragraph))

buy_signals = sorted(buy_signals, key=lambda x: x[3], reverse=True)

if not buy_signals:
    st.warning("⚠️ No strong BUY signals detected at this time.")
else:
    st.subheader(f"Top {min(20, len(buy_signals))} Strong BUY Signals ({gainer_period})")

    cols = st.columns(3)
    for idx, (coin_name, coin_symbol, coin_logo, score, rsi_score, gain, paragraph) in enumerate(buy_signals[:20]):
        with cols[idx % 3]:
            with st.container(border=True):
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.image(coin_logo, width=40)
                with col2:
                    st.markdown(f"**{coin_name} ({coin_symbol})**")
                st.metric(label="Buy Score", value=f"{score:.1f}")
                st.markdown(paragraph)
                st.markdown("📊 **Indicators Used**")
                st.markdown(f"- RSI: {rsi_score:.1f}")
                st.markdown(f"- Price Change ({gainer_period}): {gain:.2f}%")
