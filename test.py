# import requests

# try:
#     r = requests.get("https://www.nseindia.com", timeout=10)
#     print("NSE Status:", r.status_code)
# except Exception as e:
#     print("NSE ERROR:", e)

# try:
#     r = requests.get("https://finance.yahoo.com", timeout=10)
#     print("Yahoo Status:", r.status_code)
# except Exception as e:
#     print("YAHOO ERROR:", e)

import yfinance as yf
try:
    ticker = yf.Ticker("RELIANCE.NS")
    info = ticker.info
    print("YFinance Info Keys:", list(info.keys())[:10])
except Exception as e:
    print("YFinance ERROR:", e)
