import streamlit as st
from fetcher import get_top_gainers, fetch_multiple_enriched_coins

st.title("Crypto Signal Fetcher - Streamlit Test")

st.write("Fetching top 1h gainers from CoinGecko...")

try:
    gainers_1h = get_top_gainers("1h")
    st.success(f"Top 1h gainers: {gainers_1h[:5]}")

    sample_coins = gainers_1h[:5]
    st.write("Fetching enriched metadata and OHLC data...")

    all_enriched = fetch_multiple_enriched_coins(sample_coins)

    for coin_id, content in all_enriched.items():
        st.subheader(f"{coin_id.upper()}")
        meta = content["metadata"]
        if meta:
            st.image(meta.get('logo'), width=50)
            st.write(f"**Name:** {meta.get('name')}")
            st.write(f"**Symbol:** {meta.get('symbol')}")
            st.write(f"**Main Category:** {meta.get('main_category')}")
            st.write(f"**Special Tags:** {', '.join(meta.get('special_tags'))}")
            st.write(f"**Homepage:** {meta.get('homepage')}")
        else:
            st.warning("Metadata missing for this coin.")

except Exception as e:
    st.error(f"An error occurred: {e}")
