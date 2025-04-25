# main.py

from fetcher import get_top_gainers, get_ohlc_data

if __name__ == "__main__":
    gainers_1h = get_top_gainers("1h")
    print("Top 1h gainers:", gainers_1h[:5])

    sample_coin = gainers_1h[0]
    ohlc_data = get_ohlc_data(sample_coin)
    print(f"OHLC data for {sample_coin} (hourly):", ohlc_data[:2])
