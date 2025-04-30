
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
                        st.plotly_chart(fig, use_container_width=True, key='card_chart_0')

# ======== MARKET INDICATOR AT A GLANCE (v4.6.0) ========
with st.expander("📊 Market Indicator at a Glance", expanded=True):
    st.markdown("""
    <div style='background-color: #e0e0e0; padding: 10px; border-radius: 8px;'>
    """, unsafe_allow_html=True)

    btc_subscores = IndicatorEngineV2(btc_df).calculate_all() if not btc_df.empty else {}

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BTC 1h Change", f"{btc_change:+.2f}%")
        rsi_val = btc_subscores.get("RSI", "N/A")
        st.metric("RSI", f"{rsi_val if isinstance(rsi_val, (int, float)) else 'N/A'}")

    with col2:
        macd_val = btc_subscores.get("MACD", "N/A")
        st.metric("MACD", "Bullish" if macd_val == 100 else "Bearish" if macd_val == 30 else "N/A")
        ema_val = btc_subscores.get("EMA", "N/A")
        st.metric("EMA Trend", "Above 50 EMA" if ema_val == 100 else "Below 50 EMA" if ema_val == 30 else "N/A")

    with col3:
        volume_val = btc_subscores.get("Volume", "N/A")
        st.metric("Volume", "High" if volume_val == 100 else "Moderate" if volume_val == 60 else "Low" if volume_val == 30 else "N/A")

        try:
            fng_response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5).json()
            fng_value = fng_response["data"][0]["value"]
            fng_classification = fng_response["data"][0]["value_classification"]
            st.metric("Fear & Greed", f"{fng_value} ({fng_classification})")
        except:
            st.metric("Fear & Greed", "N/A")

    try:
        top_coin = next(c for c in coins if not is_stablecoin(c))
        st.markdown(f"**Top Gainer ({period}):** {top_coin['name']} +{top_coin['price_change_percentage_1h_in_currency']['usd']:.2f}%")
    except:
        st.markdown("**Top Gainer:** N/A")

        st.markdown("</div>", unsafe_allow_html=True)
# ======== END MARKET INDICATOR AT A GLANCE ========


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


st.set_page_config(page_title="Crypto Signal Dashboard v4.6.0", layout="wide")
st.title("🚀 Crypto Signal Dashboard v4.6.0 – Humanized Analysis")
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
    
            st.plotly_chart(fig, use_container_width=True, key='card_chart_1')

# ======== MARKET INDICATOR AT A GLANCE (v4.6.0) ========
with st.expander("📊 Market Indicator at a Glance", expanded=True):
    st.markdown("""
    <div style='background-color: #e0e0e0; padding: 10px; border-radius: 8px;'>
    """, unsafe_allow_html=True)

    btc_subscores = IndicatorEngineV2(btc_df).calculate_all() if not btc_df.empty else {}

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BTC 1h Change", f"{btc_change:+.2f}%")
        rsi_val = btc_subscores.get("RSI", "N/A")
        st.metric("RSI", f"{rsi_val if isinstance(rsi_val, (int, float)) else 'N/A'}")

    with col2:
        macd_val = btc_subscores.get("MACD", "N/A")
        st.metric("MACD", "Bullish" if macd_val == 100 else "Bearish" if macd_val == 30 else "N/A")
        ema_val = btc_subscores.get("EMA", "N/A")
        st.metric("EMA Trend", "Above 50 EMA" if ema_val == 100 else "Below 50 EMA" if ema_val == 30 else "N/A")

    with col3:
        volume_val = btc_subscores.get("Volume", "N/A")
        st.metric("Volume", "High" if volume_val == 100 else "Moderate" if volume_val == 60 else "Low" if volume_val == 30 else "N/A")

        try:
            fng_response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5).json()
            fng_value = fng_response["data"][0]["value"]
            fng_classification = fng_response["data"][0]["value_classification"]
            st.metric("Fear & Greed", f"{fng_value} ({fng_classification})")
        except:
            st.metric("Fear & Greed", "N/A")

    try:
        top_coin = next(c for c in coins if not is_stablecoin(c))
        st.markdown(f"**Top Gainer ({period}):** {top_coin['name']} +{top_coin['price_change_percentage_1h_in_currency']['usd']:.2f}%")
    except:
        st.markdown("**Top Gainer:** N/A")

        st.markdown("</div>", unsafe_allow_html=True)
# ======== END MARKET INDICATOR AT A GLANCE ========


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
        "analysis": paragraph,
        "buy_price": coin["current_price"],
        "buy_range": (coin["current_price"] * 0.985, coin["current_price"] * 1.015)
    })

signals = sorted(signals, key=lambda x: x["buy_score"], reverse=True)

if not signals:
    st.warning("⚠️ No qualifying signals at the moment.")
else:
    st.subheader("BUY Signals")
    cols = st.columns(3)
    





for i, sig in enumerate([s for s in signals[:20] if s['buy_score'] >= 50]):
    with cols[i % 3]:
        with st.container(border=True):
# Gradient Buy Score Bar - Visible and Functional
            fig = go.Figure()
                        fig.add_shape(type="rect", x0=0, x1=60, y0=0, y1=3, fillcolor="red", opacity=0.3, line_width=0)
            fig.add_shape(type="rect", x0=60, x1=90, y0=0, y1=3, fillcolor="yellow", opacity=0.3, line_width=0)
            fig.add_shape(type="rect", x0=90, x1=100, y0=0, y1=3, fillcolor="green", opacity=0.3, line_width=0)
                        fig.add_trace(go.Scatter(
            x=[sig['buy_score']],
            y=[1.5],
            mode='markers+text',
            marker=dict(color='black', size=12),
            text=[f"{sig['buy_score']:.1f}"],
            textposition='bottom center',
            hovertemplate="Buy Score: %{x:.1f}<extra></extra>"
            ))
                        fig.add_annotation(x=30, y=3.5, text="❌ Weak", showarrow=False, font=dict(color="red", size=12))
            fig.add_annotation(x=75, y=3.5, text="⚠️ Moderate", showarrow=False, font=dict(color="orange", size=12))
            fig.add_annotation(x=95, y=3.5, text="✅ Strong", showarrow=False, font=dict(color="green", size=12))
                        fig.update_layout(
            height=130,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[0, 100], tickvals=[0, 50, 100], tickangle=0, title=""),
            yaxis=dict(visible=False),
            plot_bgcolor="white",
            paper_bgcolor="rgba(240,240,240,0.4)",
            showlegend=False
            )
                        st.markdown("<div style='border: 1px solid #ccc; padding: 10px; border-radius: 8px;'>", unsafe_allow_html=True)
                        st.plotly_chart(fig, use_container_width=True, key='card_chart_2')

# ======== MARKET INDICATOR AT A GLANCE (v4.6.0) ========
with st.expander("📊 Market Indicator at a Glance", expanded=True):
    st.markdown("""
    <div style='background-color: #e0e0e0; padding: 10px; border-radius: 8px;'>
    """, unsafe_allow_html=True)

    btc_subscores = IndicatorEngineV2(btc_df).calculate_all() if not btc_df.empty else {}

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BTC 1h Change", f"{btc_change:+.2f}%")
        rsi_val = btc_subscores.get("RSI", "N/A")
        st.metric("RSI", f"{rsi_val if isinstance(rsi_val, (int, float)) else 'N/A'}")

    with col2:
        macd_val = btc_subscores.get("MACD", "N/A")
        st.metric("MACD", "Bullish" if macd_val == 100 else "Bearish" if macd_val == 30 else "N/A")
        ema_val = btc_subscores.get("EMA", "N/A")
        st.metric("EMA Trend", "Above 50 EMA" if ema_val == 100 else "Below 50 EMA" if ema_val == 30 else "N/A")

    with col3:
        volume_val = btc_subscores.get("Volume", "N/A")
        st.metric("Volume", "High" if volume_val == 100 else "Moderate" if volume_val == 60 else "Low" if volume_val == 30 else "N/A")

        try:
            fng_response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5).json()
            fng_value = fng_response["data"][0]["value"]
            fng_classification = fng_response["data"][0]["value_classification"]
            st.metric("Fear & Greed", f"{fng_value} ({fng_classification})")
        except:
            st.metric("Fear & Greed", "N/A")

    try:
        top_coin = next(c for c in coins if not is_stablecoin(c))
        st.markdown(f"**Top Gainer ({period}):** {top_coin['name']} +{top_coin['price_change_percentage_1h_in_currency']['usd']:.2f}%")
    except:
        st.markdown("**Top Gainer:** N/A")

        st.markdown("</div>", unsafe_allow_html=True)
# ======== END MARKET INDICATOR AT A GLANCE ========

        st.markdown("</div>", unsafe_allow_html=True)
            # GRADIENT BAR WITH LABELS AND MARKER
            fig = go.Figure()
                        # Add colored background rectangles
            fig.add_shape(type="rect", x0=0, x1=60, y0=0, y1=1, fillcolor="red", opacity=0.3, line=dict(width=0))
            fig.add_shape(type="rect", x0=60, x1=90, y0=0, y1=1, fillcolor="yellow", opacity=0.3, line=dict(width=0))
            fig.add_shape(type="rect", x0=90, x1=100, y0=0, y1=1, fillcolor="green", opacity=0.3, line=dict(width=0))
                        # Add score marker
            fig.add_shape(type="line",
            x0=sig['buy_score'],
            x1=sig['buy_score'],
            y0=0, y1=1,
            line=dict(color="black", width=4))
                        # Add text labels at appropriate positions
            fig.add_annotation(x=30, y=1.2, text="Weak", showarrow=False, font=dict(color="red", size=12))
            fig.add_annotation(x=75, y=1.2, text="Moderate", showarrow=False, font=dict(color="orange", size=12))
            fig.add_annotation(x=95, y=1.2, text="Strong", showarrow=False, font=dict(color="green", size=12))
                        # Set layout properties
            fig.update_layout(height=80,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(range=[0, 100], showticklabels=True, tickvals=[0, 50, 100], title="Buy Score"),
            yaxis=dict(visible=False),
            plot_bgcolor="white")
                                    st.plotly_chart(fig, use_container_width=True, key='card_chart_3')

# ======== MARKET INDICATOR AT A GLANCE (v4.6.0) ========
with st.expander("📊 Market Indicator at a Glance", expanded=True):
    st.markdown("""
    <div style='background-color: #e0e0e0; padding: 10px; border-radius: 8px;'>
    """, unsafe_allow_html=True)

    btc_subscores = IndicatorEngineV2(btc_df).calculate_all() if not btc_df.empty else {}

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("BTC 1h Change", f"{btc_change:+.2f}%")
        rsi_val = btc_subscores.get("RSI", "N/A")
        st.metric("RSI", f"{rsi_val if isinstance(rsi_val, (int, float)) else 'N/A'}")

    with col2:
        macd_val = btc_subscores.get("MACD", "N/A")
        st.metric("MACD", "Bullish" if macd_val == 100 else "Bearish" if macd_val == 30 else "N/A")
        ema_val = btc_subscores.get("EMA", "N/A")
        st.metric("EMA Trend", "Above 50 EMA" if ema_val == 100 else "Below 50 EMA" if ema_val == 30 else "N/A")

    with col3:
        volume_val = btc_subscores.get("Volume", "N/A")
        st.metric("Volume", "High" if volume_val == 100 else "Moderate" if volume_val == 60 else "Low" if volume_val == 30 else "N/A")

        try:
            fng_response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5).json()
            fng_value = fng_response["data"][0]["value"]
            fng_classification = fng_response["data"][0]["value_classification"]
            st.metric("Fear & Greed", f"{fng_value} ({fng_classification})")
        except:
            st.metric("Fear & Greed", "N/A")

    try:
        top_coin = next(c for c in coins if not is_stablecoin(c))
        st.markdown(f"**Top Gainer ({period}):** {top_coin['name']} +{top_coin['price_change_percentage_1h_in_currency']['usd']:.2f}%")
    except:
        st.markdown("**Top Gainer:** N/A")

        st.markdown("</div>", unsafe_allow_html=True)
# ======== END MARKET INDICATOR AT A GLANCE ========


            colA, colB = st.columns([4, 1])
            with colA:
                st.image(sig["image"], width=40)
        st.markdown(f"<div style='font-size:24px; font-weight:700'>{sig['name']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:18px; font-weight:600; color:gray'>{sig['symbol']}</div>", unsafe_allow_html=True)

            
            
            
            st.metric(label="Buy Score", value=f"{sig['buy_score']:.1f}")
            st.markdown(f"**Current Price:** <span style='font-family:sans-serif'>{fmt(sig['price'])}</span>", unsafe_allow_html=True)

            buy_low = fmt(sig['buy_range'][0])
            buy_high = fmt(sig['buy_range'][1])
            buy_range_html = f"""
<div style='font-family: sans-serif; font-size: 15px;'>
<strong>Buy Range:</strong> {buy_low} – {buy_high}
</div>
"""
            st.markdown(buy_range_html, unsafe_allow_html=True)

            subscores_html = "<ul style='padding-left: 20px;'>"
            for k, v in sig["subscores"].items():
                value = int(v) if v is not None else 'N/A'
                subscores_html += f"<li><strong>{k}:</strong> {value}</li>"
            subscores_html += "</ul>"
            st.markdown("&nbsp;", unsafe_allow_html=True)
            st.markdown("**📊 Subscores:**" + subscores_html, unsafe_allow_html=True)

            st.markdown("**🧠 Analysis:**")
            st.markdown(sig["analysis"])




