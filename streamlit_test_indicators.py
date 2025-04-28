
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import requests
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
    coins = response.json()

    if period == "1h":
        key = "price_change_percentage_1h_in_currency"
    elif period == "24h":
        key = "price_change_percentage_24h_in_currency"
    elif period == "7d":
        key = "price_change_percentage_7d_in_currency"
    else:
        key = "price_change_percentage_24h_in_currency"

    coins_sorted = sorted(
        coins,
        key=lambda x: x.get(key, 0) or 0,
        reverse=True
    )

    return [coin["id"] for coin in coins_sorted[:TOP_N_COINS]]

def get_ohlc_data_light(coin_id, vs_currency="usd", days="1"):
    url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs_currency, "days": days}
    try:
        response = requests.get(url, params=params, headers=HEADERS)
        response.raise_for_status()
        ohlc_raw = response.json()
        return [entry for entry in ohlc_raw]
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

def run_indicators(ohlc_data):
    df = pd.DataFrame(ohlc_data, columns=["timestamp", "open", "high", "low", "close"])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', errors='coerce')
    df.set_index('timestamp', inplace=True)
    if len(df) < 15:
        return None, None
    rsi = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    latest_rsi = rsi.dropna().iloc[-1] if not rsi.dropna().empty else None
    if latest_rsi is None:
        return None, None
    rsi_score = max(0, min(100, (70 - latest_rsi) * (100 / 40)))
    if rsi_score >= 70:
        signal = "BUY"
        reason = "Strong bullish technicals."
    elif 50 <= rsi_score < 70:
        signal = "WATCH"
        reason = "Moderate technicals."
    else:
        signal = "NO TRADE"
        reason = "Weak technicals."
    return rsi_score, reason if signal == "BUY" else None

st.set_page_config(page_title="Crypto Dashboard v4.5", layout="wide")
st.title("🚀 Crypto Signal Dashboard (Strong Buy Cards)")
st_autorefresh(interval=120000, key="market_sentiment_refresh")

with st.sidebar:
    scan_mode = st.radio("Choose Scanning Mode:", ("🛩️ Light Scan (Fast)", "🧠 Full Scan (Detailed)"))
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

top_coins = get_top_gainers(period=gainer_period)

if not top_coins:
    st.error("⚠️ Failed to fetch top coins. Please wait and try again.")
    st.stop()

buy_signals = []

for coin_id in top_coins:
    ohlc_data = get_ohlc_data_light(coin_id)
    if not ohlc_data:
        continue
    score, reason = run_indicators(ohlc_data)
    if score is not None and reason is not None:
        buy_signals.append((coin_id, score, reason))

buy_signals = sorted(buy_signals, key=lambda x: x[1], reverse=True)

if not buy_signals:
    st.warning("⚠️ No strong BUY signals detected at this time.")
else:
    st.subheader(f"Top {min(20, len(buy_signals))} Strong BUY Signals ({gainer_period})")
    cols = st.columns(3)
    for idx, (coin_id, score, reason) in enumerate(buy_signals[:20]):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"### 🪙 {coin_id.capitalize()}")
                st.metric(label="Total Score", value=f"{score:.2f}")
                st.success(f"✅ {reason}")
