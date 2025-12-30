import requests
import pandas as pd
from bs4 import BeautifulSoup
from utils.logger import get_logger

logger = get_logger("company_data")

def fetch_screener_page(symbol):
    urls = [
        f"https://www.screener.in/company/{symbol}/consolidated/",
        f"https://www.screener.in/company/{symbol}/",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    BASE_URL = "https://www.screener.in/company/{symbol}/"

    HE

    for url in urls:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200 and "Login" not in res.text and "rate limited" not in res.text:
            return res.text

    return None


# ---------------- SAFE CLEANING ---------------- #
def to_num(x):
    try:
        if x is None:
            return None
        x = str(x)
        x = x.replace("₹", "").replace(",", "").replace("%", "").strip()
        if x in ["", "-", "—", "None", "nan", "NaN"]:
            return None
        return float(x)
    except:
        return None


def normalize_table(df):
    df = df.copy()

    if df.columns[0] != "Particulars":
        df.columns = ["Particulars"] + list(df.columns[1:])

    df["Particulars"] = (
        df["Particulars"]
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.lower()
    )

    return df.set_index("Particulars", drop=True)


def find_row(df, candidates):
    try:
        idx = df.index.astype(str)
        for c in candidates:
            c = c.lower().strip()
            match = idx[idx.str.contains(c)]
            if len(match):
                return df.loc[match.index[0]]
        return None
    except:
        return None


# ---------------- MAIN SCRAPER ---------------- #
def get_company_summary(symbol: str):
    try:
        url = BASE_URL.format(symbol=symbol.upper())
        res = requests.get(url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            logger.error(f"Screener returned {res.status_code} for {symbol}")
            return None

        soup = BeautifulSoup(res.text, "html.parser")
        info = {}

        # ----------- TOP METRICS ----------- #
        stats = soup.find_all("li", {"class": "flex flex-space-between"})
        for s in stats:
            try:
                key = s.find("span").text.strip()
                val = s.find("span", {"class": "number"}).text.strip()

                if "Stock P/E" in key:
                    info["trailingPE"] = to_num(val)

                if "Book Value" in key:
                    info["priceToBook"] = to_num(val)

                if "ROE" in key:
                    roe = to_num(val)
                    info["returnOnEquity"] = (roe / 100.0) if roe else None

                if "Market Cap" in key:
                    mc = to_num(val)
                    info["marketCap"] = mc * 1e7 if mc else None

            except:
                pass

        # ----------- TABLES ----------- #
        tables = pd.read_html(res.text)

        if len(tables) < 3:
            logger.error("Screener layout changed — tables missing")
            return None

        financials = normalize_table(tables[0])
        balance_sheet = normalize_table(tables[1])
        cashflow = normalize_table(tables[2])

        logger.info(f"P&L table identified")
        logger.info(f"Balance Sheet identified")
        logger.info(f"Cash Flow identified")

        # ----------- ROW EXTRACTION ----------- #
        sales_row = find_row(financials, ["sales", "revenue"])
        np_row = find_row(financials, ["net profit", "pat"])
        op_row = find_row(financials, ["operating profit", "ebit"])
        eps_row = find_row(financials, ["eps"])

        debt_row = find_row(balance_sheet, ["borrowings", "total debt"])
        reserves_row = find_row(balance_sheet, ["reserves"])

        ocf_row = find_row(cashflow, ["cash from operating activity"])
        capex_row = find_row(cashflow, ["capital expenditure"])

        info["revenueGrowth"] = None
        info["earningsGrowth"] = None
        info["operatingMargins"] = None
        info["totalStockholderEquity"] = None
        info["freeCashflow"] = None

        # Revenue growth
        try:
            v = [to_num(v) for v in sales_row.tail(3).values]
            if v[0] and v[-1] and v[0] > 0:
                info["revenueGrowth"] = (v[-1] - v[0]) / v[0] * 100
        except:
            logger.warning("Revenue growth unavailable")

        # Profit growth
        try:
            v = [to_num(v) for v in np_row.tail(3).values]
            if v[0] and v[-1] and v[0] > 0:
                info["earningsGrowth"] = (v[-1] - v[0]) / v[0] * 100
        except:
            logger.warning("Profit growth unavailable")

        # Operating Margin
        try:
            op = to_num(op_row.tail(1).values[0])
            sales = to_num(sales_row.tail(1).values[0])
            info["operatingMargins"] = (op / sales) * 100 if sales else None
        except:
            logger.warning("Operating margin unavailable")

        try:
            info["totalStockholderEquity"] = to_num(reserves_row.tail(1).values[0])
        except:
            logger.warning("Equity unavailable")

        try:
            ocf = to_num(ocf_row.tail(1).values[0])
            capex = abs(to_num(capex_row.tail(1).values[0])) if capex_row is not None else 0
            info["freeCashflow"] = ocf - capex if ocf else None
        except:
            logger.warning("FCF unavailable")

        logger.info(f"Screener data loaded successfully for {symbol}")

        return {
            "symbol": symbol.upper(),
            "info": info,
            "financials": financials,
            "balance_sheet": balance_sheet,
            "cashflow": cashflow
        }

    except Exception as e:
        logger.error(f"Company data fetch failed: {e}")
        return None
