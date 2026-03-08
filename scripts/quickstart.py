"""Quick Start Guide — validates your setup before trading.

Usage:
  python scripts/quickstart.py              # Interactive setup check
  python scripts/quickstart.py --exchange bybit  # Check specific exchange
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_dependencies():
    """Check all required packages are installed."""
    print("\n[1/5] Checking dependencies...")
    missing = []
    for pkg in ["ccxt", "pandas", "numpy", "pandas_ta", "yaml", "tabulate"]:
        try:
            __import__(pkg)
            print(f"  + {pkg}")
        except ImportError:
            print(f"  - {pkg} MISSING")
            missing.append(pkg)

    if missing:
        print(f"\n  Install missing: pip install {' '.join(missing)}")
        return False
    print("  All dependencies OK!")
    return True


def check_exchange_connection(exchange_name="bybit"):
    """Test exchange connectivity (public API, no keys needed)."""
    print(f"\n[2/5] Testing {exchange_name} connection...")
    import ccxt

    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({"enableRateLimit": True})
        exchange.load_markets()
        print(f"  Connected! {len(exchange.markets)} markets available")

        # Check if BTC/USDT perpetual exists
        perp_symbol = "BTC/USDT:USDT"
        if perp_symbol in exchange.markets:
            print(f"  {perp_symbol} perpetual futures: Available")
            m = exchange.market(perp_symbol)
            print(f"  Min order: {m.get('limits', {}).get('cost', {}).get('min', '?')} USDT")
        else:
            # Try alternative symbol format
            alt = "BTC/USDT"
            if alt in exchange.markets:
                print(f"  {alt} found (may need different symbol format for futures)")
            else:
                print(f"  Warning: BTC/USDT not found on {exchange_name}")

        return True
    except Exception as e:
        print(f"  Connection failed: {e}")
        return False


def check_market_data(exchange_name="bybit"):
    """Fetch sample OHLCV data to verify data access."""
    print(f"\n[3/5] Fetching market data from {exchange_name}...")
    import ccxt

    try:
        exchange_class = getattr(ccxt, exchange_name)
        exchange = exchange_class({
            "enableRateLimit": True,
            "options": {"defaultType": "swap"},
        })
        exchange.load_markets()

        # Try perpetual symbol formats
        for symbol in ["BTC/USDT:USDT", "BTC/USDT"]:
            if symbol in exchange.markets:
                ohlcv = exchange.fetch_ohlcv(symbol, "4h", limit=50)
                if ohlcv:
                    print(f"  Got {len(ohlcv)} candles for {symbol}")
                    last = ohlcv[-1]
                    print(f"  Latest BTC price: ${last[4]:,.2f}")
                    print(f"  24h volume sample: {last[5]:,.0f}")
                    return True

        print("  Could not fetch OHLCV data")
        return False
    except Exception as e:
        print(f"  Data fetch failed: {e}")
        return False


def check_config():
    """Check if config file exists."""
    print("\n[4/5] Checking configuration...")
    config_path = "config/config.yaml"
    testnet_path = "config/config.testnet.yaml"

    if os.path.exists(config_path):
        print(f"  config.yaml found")
        # Check it doesn't have real keys committed
        with open(config_path) as f:
            content = f.read()
            if "YOUR_API" in content:
                print("  Warning: API keys not configured yet")
            else:
                print("  API keys configured")
    else:
        print(f"  config.yaml not found")
        print(f"  Copy config.example.yaml or config.testnet.yaml to config.yaml")

    if os.path.exists(testnet_path):
        print(f"  config.testnet.yaml found (testnet config ready)")

    return True


def show_fee_comparison():
    """Show why futures matter for small accounts."""
    print("\n[5/5] Fee impact analysis for $100 capital...")
    print()
    print("  +--------------------------------------------------+")
    print("  |          SPOT vs FUTURES FEE COMPARISON          |")
    print("  +--------------------------------------------------+")
    print("  |                    Spot      Futures             |")
    print("  |  Taker fee:       0.10%      0.055%              |")
    print("  |  Maker fee:       0.10%      0.020%              |")
    print("  |  Round trip:      0.20%      0.040% (maker)      |")
    print("  |                                                  |")
    print("  |  $30 trade cost:  $0.06      $0.012              |")
    print("  |  Annual (520x):   $31.20     $6.24               |")
    print("  |  % of $100:       31.2%      6.2%                |")
    print("  |                                                  |")
    print("  |  Verdict: Futures saves $25/year on fees alone   |")
    print("  |  That's 25% more capital working for you!        |")
    print("  +--------------------------------------------------+")
    print()
    print("  Recommendation: ALWAYS use futures + maker (limit) orders")


def show_next_steps():
    print("\n" + "=" * 55)
    print("  NEXT STEPS")
    print("=" * 55)
    print("""
  1. Register on Bybit (or OKX/Binance)
  2. Get API Key (read + trade permissions, NO withdrawal)
  3. Copy config/config.testnet.yaml to config/config.yaml
  4. Fill in your API key and secret
  5. Run paper trading first:

     python -m src --config config/config.yaml

  6. After 2+ weeks of paper trading, if profitable:
     Change mode: "paper" -> "live" in config.yaml

  IMPORTANT:
  - Start with sandbox: true (testnet mode)
  - Never enable withdrawal permission on API key
  - Never share your API secret
  - Paper trade for at least 2 weeks before going live
""")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Trading Bot Quick Start")
    parser.add_argument("--exchange", default="bybit", help="Exchange to test")
    args = parser.parse_args()

    print("=" * 55)
    print("  CRYPTO TRADING BOT — QUICK START CHECK")
    print("=" * 55)

    ok = True
    ok = check_dependencies() and ok
    ok = check_exchange_connection(args.exchange) and ok
    ok = check_market_data(args.exchange) and ok
    check_config()
    show_fee_comparison()

    if ok:
        print("\n  All checks PASSED! Your system is ready.")
    else:
        print("\n  Some checks FAILED. Fix the issues above first.")

    show_next_steps()


if __name__ == "__main__":
    main()
