# main.py - v1.2

from fetcher import get_top_gainers, fetch_multiple_ohlc

if __name__ == "__main__":
    gainers_1h = get_top_gainers("1h")
    print("\nTop 1h gainers:", gainers_1h[:5])

    sample_coins = gainers_1h[:5]  # Just fetch OHLC for 5 coins for demo
    all_ohlc_data = fetch_multiple_ohlc(sample_coins)
    print("\nSample OHLC data:", {coin: data[:2] for coin, data in all_ohlc_data.items()})
