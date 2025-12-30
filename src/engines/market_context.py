import pandas as pd
from utils.logger import get_logger
from data.market_data import (
    get_nse_index_history,
    get_price_history
)

logger = get_logger("market_context")

BENCHMARKS = {
    "NIFTY50": "NIFTY 50",
    "BANKNIFTY": "NIFTY BANK",
    "S&P500": "SPY"
}


def calculate_trend(df: pd.DataFrame):
    if df is None or df.empty:
        return "unknown", 0

    # NSE JSON path
    if "ChangePercent" in df.columns:
        pct = float(df.iloc[0]["ChangePercent"])

    # TwelveData path
    else:
        close = df["Close"]
        pct = ((close.iloc[-1] - close.iloc[0]) / close.iloc[0]) * 100

    if pct > 10:
        return "strong_bullish", pct
    elif pct > 3:
        return "bullish", pct
    elif pct < -10:
        return "strong_bearish", pct
    elif pct < -3:
        return "bearish", pct
    else:
        return "sideways", pct


def get_market_context():
    results = {}

    # =========================
    # INDIA — NSE JSON
    # =========================
    nifty = get_nse_index_history("NIFTY 50")
    trend, change = calculate_trend(nifty)
    results["NIFTY50"] = {
        "trend": trend,
        "change_percent": round(change, 2)
    }

    banknifty = get_nse_index_history("NIFTY BANK")
    trend, change = calculate_trend(banknifty)
    results["BANKNIFTY"] = {
        "trend": trend,
        "change_percent": round(change, 2)
    }

    # =========================
    # USA — TwelveData
    # =========================
    spx = get_price_history("SPY")
    trend, change = calculate_trend(spx)
    results["S&P500"] = {
        "trend": trend,
        "change_percent": round(change, 2)
    }

    for k in results:
        results[k]["volatility"] = get_volatility_regime(results[k]["change_percent"])

    breadth = compute_market_breadth(results)
    confidence = compute_confidence(results)
    summary = build_summary(results, breadth, confidence)


    return {
    "indices": results,
    "market_breadth": breadth,
    "confidence": confidence,
    "summary": summary
}

def get_volatility_regime(pct: float):
    pct = abs(pct)

    if pct < 1:
        return "calm"
    elif pct < 3:
        return "normal"
    elif pct < 6:
        return "high_volatility"
    else:
        return "panic"
    
def compute_market_breadth(results):
    trends = [results[k]["trend"] for k in results]

    bull = sum(t.startswith("bull") for t in trends)
    bear = sum(t.startswith("bear") for t in trends)

    if bull == 3:
        return "strong_bull_market"
    if bull >= 2:
        return "bullish"
    if bear == 3:
        return "strong_bear_market"
    if bear >= 2:
        return "bearish"
    
    return "sideways"

def compute_confidence(results):
    valid = sum(results[k]["trend"] != "unknown" for k in results)
    volatility = [results[k]["volatility"] for k in results if "volatility" in results[k]]

    if valid == 3 and all(v in ["calm", "normal"] for v in volatility):
        return "high"
    if valid >= 2:
        return "medium"
    return "low"

def build_summary(results, breadth, confidence):
    nifty = results["NIFTY50"]
    bank = results["BANKNIFTY"]
    spx  = results["S&P500"]

    summary = []

    summary.append(f"NIFTY shows {nifty['trend']} momentum ({nifty['change_percent']}%).")
    summary.append(f"BankNifty is {bank['trend']} ({bank['change_percent']}%).")
    summary.append(f"US markets remain {spx['trend']} ({spx['change_percent']}%).")

    summary.append(f"Overall breadth is {breadth.replace('_', ' ')} with {confidence} confidence.")

    return " ".join(summary)



