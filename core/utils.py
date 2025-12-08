from collections import defaultdict

POPULAR_NAMES = {
    "BTC": "Bitcoin",
    "ETH": "Ethereum",
    "BNB": "Binance Coin",
    "SOL": "Solana",
    "XRP": "Ripple",
    "DASH": "Dash",
    "ZEC": "Zcash",
    "FDUSD": "First Digital USD (Stablecoin)",
    "USDC": "USD Coin (Stablecoin)",
    "ASTER": "Astar",
    "DOT": "Polkadot",
    "ADA": "Cardano",
    "DOGE": "Dogecoin",
    "TRX": "Tron",
    "SHIB": "Shiba Inu",
    "AVAX": "Avalanche",
}

def format_volume(num):
    num = float(num)

    if abs(num) >= 1_000_000_000:
        raw = f"{num / 1_000_000_000:,.2f}B"
    elif abs(num) >= 1_000_000:
        raw = f"{num / 1_000_000:,.2f}M"
    elif abs(num) >= 1_000:
        raw = f"{num / 1_000:,.2f}K"
    else:
        return f"{num:,.0f}".replace('.', '#').replace(',', '.').replace('#', ',')

    return raw.replace('.', '#').replace(',', '.').replace('#', ',')
