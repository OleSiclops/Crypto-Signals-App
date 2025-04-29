
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
import ta
from streamlit_autorefresh import st_autorefresh
from indicator_engine_v2 import IndicatorEngineV2

COINGECKO_API_BASE = "https://pro-api.coingecko.com/api/v3"
TOP_N_COINS = 50
HEADERS = {"x-cg-pro-api-key": st.secrets["general"]["COINGECKO_API_KEY"]}

def fetch_btc_24h_prices():
    url = f"{COINGECKO_API_BASE}/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1"}
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json().get("prices", [])
        df = pd.DataFrame(data, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except Exception as e:
        st.warning("⚠️ Failed to fetch BTC 24h prices. Skipping chart...")
        return pd.DataFrame()

def get_btc_market_sentiment():
    url = f"{COINGECKO_API_BASE}/coins/bitcoin"
    params = {"localization": "false", "tickers": "false", "market_data": "true"}
    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data['market_data']['price_change_percentage_1h_in_currency']['usd']
    except:
        st.warning("⚠️ Failed to fetch BTC sentiment. Showing neutral gauge.")
        return 0.0

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
    response = requests.get(url, params=params, headers=HEADERS, timeout=5)
    response.raise_for_status()
    return response.json()

def get_ohlc_data(coin_id, use_market_chart=False, vs_currency="usd", days="1"):
    if use_market_chart:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/market_chart"
        params = {"vs_currency": vs_currency, "days": days}
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=5)
            response.raise_for_status()
            prices = response.json().get("prices", [])
            volumes = response.json().get("total_volumes", [])
            df = pd.DataFrame(prices, columns=["timestamp", "price"])
            df["volume"] = [v[1] for v in volumes]
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df["open"] = df["high"] = df["low"] = df["close"] = df["price"]
            return df[["timestamp", "open", "high", "low", "close", "volume"]]
        except:
            return pd.DataFrame()
    else:
        url = f"{COINGECKO_API_BASE}/coins/{coin_id}/ohlc"
        params = {"vs_currency": vs_currency, "days": days}
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=5)
            response.raise_for_status()
            ohlc = response.json()
            df = pd.DataFrame(ohlc, columns=["timestamp", "open", "high", "low", "close"])
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except:
            return pd.DataFrame()

def plot_btc_chart(df):
    if df.empty:
        st.warning("No BTC price data to display.")
        return
    df.set_index("timestamp", inplace=True)
    df["SMA_12h"] = df["price"].rolling(window=12).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["price"], mode="lines", name="BTC Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["SMA_12h"], mode="lines", name="12h SMA", line=dict(dash="dot")))
    fig.update_layout(title="BTC 24h Price Chart with 12h SMA", height=350)
    st.plotly_chart(fig, use_container_width=True)

def generate_human_analysis(coin, scores):
    phrases = []
    if scores["RSI"] is not None:
        if scores["RSI"] > 75:
            phrases.append(f"RSI suggests {coin} may be approaching overbought territory.")
        elif scores["RSI"] < 30:
            phrases.append(f"{coin} appears oversold on RSI, indicating potential upside.")
        else:
            phrases.append(f"RSI for {coin} is neutral, showing room for movement.")

    if scores["MACD"] == 100:
        phrases.append("MACD just crossed bullishly, a classic buy trigger.")
    elif scores["MACD"] == 30:
        phrases.append("MACD is flat or bearish, offering no clear signal.")

    if scores["EMA"] == 100:
        phrases.append(f"{coin} is trading above its 50 EMA, suggesting bullish momentum.")
    elif scores["EMA"] == 30:
        phrases.append(f"{coin} is trending below its 50 EMA, which may act as resistance.")

    if scores["Volume"] is not None:
        if scores["Volume"] >= 100:
            phrases.append("Volume is surging above average, confirming strong interest.")
        elif scores["Volume"] >= 60:
            phrases.append("Volume is slightly above average, supporting the move.")
        else:
            phrases.append("Current volume is below average, so momentum may be lacking.")

    if scores["ADX"] is not None:
        if scores["ADX"] >= 60:
            phrases.append("ADX shows the trend is gaining strength.")
        else:
            phrases.append("ADX suggests trend strength is moderate or weak.")

    return " ".join(random.sample(phrases, min(4, len(phrases))))


def fmt(price):
    if price >= 1:
        return f"${price:.2f}"
    elif price >= 0.1:
        return f"${price:.3f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    else:
        return f"${price:.5f}"


st.set_page_config(page_title="Crypto Signal Dashboard v4.5.6", layout="wide")
st.title("🚀 Crypto Signal Dashboard v4.5.6 – Humanized Analysis")
st_autorefresh(interval=120000, key="market_sentiment_refresh")

col1, col2 = st.columns([2, 1])
with col1:
    btc_df = fetch_btc_24h_prices()
    plot_btc_chart(btc_df)
with col2:
    btc_change = get_btc_market_sentiment()
    btc_gauge = (max(-5.0, min(5.0, btc_change)) + 5) * 10
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=btc_gauge,
        number={'suffix': "%"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "black"},
               'steps': [{'range': [0, 33], 'color': "red"},
                         {'range': [33, 66], 'color': "yellow"},
                         {'range': [66, 100], 'color': "green"}]},
        title={'text': "BTC 1h Sentiment"}
    ))
    st.plotly_chart(fig, use_container_width=True)

with st.sidebar:
    scan_mode = st.radio("Scan Mode:", ["🛩️ Light (1h)", "🧠 Full (4h)"])
    period = st.radio("Top Gainers Period:", ["1h", "24h", "7d"])

use_market_chart = "Full" in scan_mode
coins = get_top_gainers(period=period)
signals = []


def is_stablecoin(coin):
    stable_keywords = ["usd", "usdt", "usdc", "tether", "dai", "busd", "stable"]
    name = coin['name'].lower()
    symbol = coin['symbol'].lower()
    return any(word in name or word in symbol for word in stable_keywords)

for coin in coins:
    if is_stablecoin(coin):
        continue

    df = get_ohlc_data(coin['id'], use_market_chart=use_market_chart)
    if df.empty or len(df) < 15:
        continue

    engine = IndicatorEngineV2(df)
    subscores = engine.calculate_all()
    buy_score = engine.calculate_weighted_score()
    paragraph = generate_human_analysis(coin['name'], subscores)

    signals.append({
        "name": coin["name"],
        "symbol": coin["symbol"].upper(),
        "image": coin["image"],
        "price": coin["current_price"],
        "gain": coin.get(f"price_change_percentage_{period}_in_currency", 0.0),
        "buy_score": buy_score,
        "subscores": subscores,
        "analysis": paragraph
    })

signals = sorted(signals, key=lambda x: x["buy_score"], reverse=True)

if not signals:
    st.warning("⚠️ No qualifying signals at the moment.")
else:
    st.subheader(f"Top {min(20, len(signals))} BUY Signals")
    cols = st.columns(3)
    for i, sig in enumerate(signals[:20]):
        with cols[i % 3]:
            with st.container(border=True):
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.image(sig["image"], width=40)
                with col2:
                    st.markdown(f"**{sig['name']} ({sig['symbol']})**")
                
    score = sig['buy_score']
    if score >= 75:
        st.markdown("🔥 **Strong Buy – Buy Now**")
    elif score >= 60:
        st.markdown("✅ **Moderate Buy**")
    else:
        st.markdown("⚠️ **Weak Signal – Hold**")
    st.metric(label="Buy Score", value=f"{score:.1f}")

                                
    st.metric(label="Change", value=f"{sig['gain']:.2f}%")

    # Dynamic price formatting based on value
    def fmt(price):
        if price >= 1: return f"${price:.2f}"
        elif price >= 0.1: return f"${price:.3f}"
        elif price >= 0.01: return f"${price:.4f}"
        else: return f"${price:.5f}"

    st.markdown(f"**Buy Price:** {fmt(sig['buy_price'])}")
    st.markdown(f"**Buy Range:** {fmt(sig['buy_range'][0])} – {fmt(sig['buy_range'][1])}")

                st.markdown("**📊 Subscores:** " + ", ".join([f"{k}: {int(v) if v is not None else 'N/A'}" for k, v in sig["subscores"].items()]))
                st.markdown("**🧠 Analysis:**")
                st.markdown(sig["analysis"])
