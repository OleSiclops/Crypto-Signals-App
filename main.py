# main.py - v1.4

from fetcher import get_top_gainers, fetch_multiple_enriched_coins

if __name__ == "__main__":
    gainers_1h = get_top_gainers("1h")
    print("\nTop 1h gainers:", gainers_1h[:5])

    sample_coins = gainers_1h[:5]
    all_enriched = fetch_multiple_enriched_coins(sample_coins)

    for coin_id, content in all_enriched.items():
        print(f"\n{coin_id.upper()} Metadata:")
        meta = content["metadata"]
        print(f"  Name: {meta.get('name')}")
        print(f"  Symbol: {meta.get('symbol')}")
        print(f"  Main Category: {meta.get('main_category')}")
        print(f"  Special Tags: {meta.get('special_tags')}")
        print(f"  Logo: {meta.get('logo')}")
        print(f"  Homepage: {meta.get('homepage')}")
