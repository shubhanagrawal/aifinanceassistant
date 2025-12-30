# data/nse_session.py
import requests
from utils.logger import get_logger

logger = get_logger("nse_session")

NSE_HOME = "https://www.nseindia.com"
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def bootstrap_session():
    """Create and bootstrap NSE session"""
    session = requests.Session()
    try:
        session.get(NSE_HOME, headers=NSE_HEADERS, timeout=10)
        logger.info("NSE session bootstrapped")
        return session
    except Exception as e:
        logger.error(f"Failed to bootstrap: {e}")
        return session