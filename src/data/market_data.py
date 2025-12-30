import requests
import pandas as pd
from utils.logger import get_logger
import os

logger = get_logger("market_data")

# ================================
#  ENV + CONFIG
# ================================
TWELVEDATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}


# ================================
#  NSE API FUNCTIONS
# ================================
def get_nse_indices():
    """
    Fetches all NSE indices JSON.
    Returns list of index objects or None.
    """
    try:
        url = "https://www.nseindia.com/api/allIndices"
        session = requests.Session()
        session.headers.update(NSE_HEADERS)

        # Visit homepage first to generate cookies
        session.get("https://www.nseindia.com", timeout=5)

        res = session.get(url, timeout=5)
        res.raise_for_status()

        data = res.json()
        return data.get("data", [])

    except Exception as e:
        logger.error(f"NSE fetch failed: {e}")
        return None


def get_nse_index_history(index_name: str):
    """
    Returns pseudo-historical DataFrame
    For now, NSE only gives snapshot, so we use ChangePercent
    """
    indices = get_nse_indices()
    if not indices:
        return None

    for idx in indices:
        if idx["index"] == index_name:
            df = pd.DataFrame([{
                "Index": idx["index"],
                "Close": idx["last"],
                "ChangePercent": idx["percentChange"]
            }])
            return df

    logger.warning(f"No NSE index found for {index_name}")
    return None


# ================================
#  TWELVE DATA FUNCTIONS
# ================================
def get_price_history(symbol: str):
    """
    Fetch market history from TwelveData
    Returns pandas DataFrame or None
    """

    if not TWELVEDATA_API_KEY:
        logger.error("Missing TWELVEDATA_API_KEY in environment")
        return None

    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": 30,
        "apikey": TWELVEDATA_API_KEY
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()

        data = res.json()

        if "values" not in data:
            logger.warning(f"No data returned for {symbol}: {data}")
            return None

        df = pd.DataFrame(data["values"])
        df["close"] = df["close"].astype(float)
        df.rename(columns={"close": "Close"}, inplace=True)

        df = df.iloc[::-1].reset_index(drop=True)  # oldest → newest
        return df

    except Exception as e:
        logger.error(f"TwelveData fetch failed for {symbol}: {e}")
        return None
