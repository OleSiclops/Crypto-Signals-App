
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import random
import ta

st.set_page_config(page_title="Crypto Signal Dashboard v4.5.6", layout="wide")
from streamlit_autorefresh import st_autorefresh
from indicator_engine_v2 import IndicatorEngineV2
st.title("🚀 Crypto Signal Dashboard v4.5.6 – Humanized Analysis")

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






# --- MARKET INDICATOR SNAPSHOT ---
with st.expander("🧭 Market Indicator at a Glance", expanded=True):
    from fetcher import get_ohlc_data
    from indicator_engine_v2 import IndicatorEngineV2
    import plotly.graph_objects as go

    import pandas as pd
    data = get_ohlc_data("bitcoin", days=1)
    df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close"])
    if df.empty:
        st.error("⚠️ Failed to load BTC data. Check your CoinGecko access or API key.")
        st.stop()
    engine = IndicatorEngineV2(df)

    def draw_indicator_bar(label, value, colors, marker_label="", tooltip=""):
        fig = go.Figure()
        last = 0
        for color, end in colors:
            fig.add_shape(type="rect", x0=last, x1=end, y0=0, y1=3,
                          fillcolor=color, opacity=0.3, line_width=0)
            last = end
        fig.add_shape(type="line", x0=value, x1=value, y0=0, y1=3, line=dict(color="black", width=4))
        fig.update_layout(height=60, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis=dict(range=[0, 100], visible=False),
                          yaxis=dict(visible=False),
                          plot_bgcolor="white", paper_bgcolor="rgba(0,0,0,0)")
        icon_html = f"<span title='{tooltip}' style='cursor: help;'> ℹ️</span>"
        st.markdown(f"**{label}:** {marker_label or str(round(value, 2))}" + icon_html, unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        btc_change = ((df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]) * 100
        draw_indicator_bar("BTC 1h Change", btc_change, [("red", 33), ("yellow", 66), ("green", 100)],
                           f"{btc_change:.2f}%", "Raw price change % over 1 hour.")

        sentiment = min(100, max(0, btc_change + 50))
        draw_indicator_bar("BTC 1h Sentiment", sentiment, [("red", 33), ("yellow", 66), ("green", 100)],
                           f"{sentiment:.0f}", "Bullish sentiment scored from BTC 1h move.")

        rsi = engine.calculate_rsi() or 0
        draw_indicator_bar("RSI", rsi, [("red", 33), ("yellow", 66), ("green", 100)],
                           f"{rsi:.2f}", "BTC Relative Strength Index. >70 = overbought.")

        vol = engine.calculate_volume_spike() or 0
        draw_indicator_bar("Volume", vol, [("red", 33), ("yellow", 66), ("green", 100)],
                           f"{vol:.0f}", "Volume spike vs. average.")

    with col2:
        macd = 100 if engine.calculate_macd() == "Bullish" else 0
        draw_indicator_bar("MACD", macd, [("red", 50), ("blue", 100)],
                           "Bullish" if macd else "Bearish", "MACD crossover trend.")

        ema = 100 if engine.calculate_ema_trend() == "Bullish" else 0
        draw_indicator_bar("EMA Trend", ema, [("red", 50), ("green", 100)],
                           "Bullish" if ema else "Bearish", "Price vs. EMA50.")

        draw_indicator_bar("Fear & Greed", 53, [("red", 33), ("yellow", 66), ("green", 100)],
                           "53", "Static mock of market sentiment.")

        stoch = engine.calculate_stoch_rsi() or 0
        draw_indicator_bar("StochRSI", stoch, [("red", 33), ("yellow", 66), ("green", 100)],
                           f"{stoch:.2f}", "Stochastic RSI sensitivity.")
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


st_autorefresh(interval=120000, key="market_sentiment_refresh")


btc_df = fetch_btc_24h_prices()
plot_btc_chart(btc_df)

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
    





for i, sig in enumerate([s for s in signals[:20] if s['buy_score'] >= 60]):
    with cols[i % 3]:
        with st.container(border=True):
# Gradient Buy Score Bar - Visible and Functional
            import plotly.graph_objects as go
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
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            # GRADIENT BAR WITH LABELS AND MARKER
            import plotly.graph_objects as go
            fig = go.Figure()

            # Add colored background rectangles
            fig.add_shape(type="rect", x0=0, x1=60, y0=0, y1=3, fillcolor="red", opacity=0.3, line=dict(width=0))
            fig.add_shape(type="rect", x0=60, x1=90, y0=0, y1=3, fillcolor="yellow", opacity=0.3, line=dict(width=0))
            fig.add_shape(type="rect", x0=90, x1=100, y0=0, y1=3, fillcolor="green", opacity=0.3, line=dict(width=0))

            # Add score marker
            fig.add_shape(type="line",
                          x0=sig['buy_score'],
                          x1=sig['buy_score'],
                          y0=0, y1=3,
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

            st.plotly_chart(fig, use_container_width=True)

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





