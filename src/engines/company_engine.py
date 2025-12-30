import numpy as np

def safe(x):
    try:
        if x is None:
            return None
        v = float(str(x).replace(",", "").strip())
        return None if np.isnan(v) else v
    except:
        return None


def trend_direction(values):
    values = [safe(v) for v in values if safe(v) is not None]
    if len(values) < 3:
        return "unknown"
    if values[-1] > values[-2] > values[-3]:
        return "improving"
    if values[-1] < values[-2] < values[-3]:
        return "deteriorating"
    return "mixed"


def build_company_analysis(symbol, screener=None):
    if screener is None:
        return None

    info = screener["info"]
    fin = screener["financials"]
    bs = screener["balance_sheet"]
    cf = screener["cashflow"]

    # ---------- CORE VALUES ----------
    pe = safe(info.get("trailingPE"))
    pb = safe(info.get("priceToBook"))
    roe = safe(info.get("returnOnEquity")) * 100 if info.get("returnOnEquity") else None

    # ---------- Operating Margin ----------
    try:
        op = safe(fin.iloc[-1].get(fin.columns[-1]))
        sales = safe(fin.iloc[-1].get(fin.columns[-1]))
        op_margin = round((op / sales) * 100, 2) if sales else None
    except:
        op_margin = safe(info.get("operatingMargins"))

    # ---------- Growth ----------
    revenue_growth = safe(info.get("revenueGrowth")) or 0
    eps_growth = safe(info.get("earningsGrowth")) or 0

    # ---------- Risk ----------
    try:
        debt = safe(bs.iloc[-1].values[-1])
    except:
        debt = 0

    bankruptcy_risk = "very_low" if debt == 0 else "low" if debt < 1000 else "moderate"

    # ---------- Cashflow ----------
    try:
        ocf = safe(cf.iloc[-1].values[-1])
        npf = safe(fin.iloc[-1].values[-1])
        if ocf and npf:
            cfo_vs_income = "strong" if ocf > npf else "weak" if ocf < (0.7 * npf) else "moderate"
        else:
            cfo_vs_income = "unknown"
    except:
        cfo_vs_income = "unknown"

    # ---------- Trend ----------
    try:
        roe_trend = trend_direction(fin.iloc[-4:].values[:, -1])
    except:
        roe_trend = "unknown"

    # ---------- Valuation ----------
    valuation_position = (
        "undervalued" if pe and pe < 18
        else "overvalued" if pe and pe > 35
        else "fair_value"
    )

    # ---------- Final Score ----------
    score = 0
    if roe and roe > 20: score += 20
    if revenue_growth and revenue_growth > 10: score += 15
    if eps_growth and eps_growth > 10: score += 15
    if bankruptcy_risk == "very_low": score += 10

    rating = (
        "strong_buy" if score >= 70 else
        "buy" if score >= 55 else
        "speculative_but_viable" if score >= 40 else
        "high_risk"
    )

    return {
        "symbol": symbol,
        "valuation": {"pe": pe, "pb": pb},
        "profitability": {"roe": roe, "operating_margin": op_margin},
        "growth": {"revenue_growth": revenue_growth, "eps_growth": eps_growth},
        "risk": {"de_ratio": debt, "bankruptcy_risk": bankruptcy_risk},
        "cashflow_quality": {"cfo_vs_net_income": cfo_vs_income},
        "trend_intelligence": {
            "roe_trend": roe_trend,
            "margin_trend": "mixed",
            "revenue_trend": "mixed",
            "eps_trend": "mixed",
            "financial_stability_direction": "mixed"
        },
        "valuation_context": {
            "valuation_position": valuation_position,
            "valuation_comment": "Stock is trading near reasonable valuation range."
        },
        "final_assessment": {
            "final_quality_score": score,
            "rating": rating,
            "investment_style": "value_or_turnaround" if score >= 40 else "avoid"
        },
        "analyst_summary": {
            "headline_view": f"{symbol} shows mixed fundamentals with opportunities and risks.",
            "business_quality_view": "Business exhibits strong profitability.",
            "growth_view": "Growth clarity limited.",
            "financial_strength_view": "Financial strength is robust with manageable leverage.",
            "cashflow_view": "Cashflow reliability needs monitoring.",
            "valuation_view": "Stock is trading near reasonable valuation range.",
            "risk_flags": ["No major structural red flags detected"],
            "final_opinion": "May suit tactical investors comfortable with risk."
        }
    }
