import streamlit as st
import requests

st.set_page_config(
    page_title="AI Financial Assistant",
    layout="wide"
)

BACKEND_URL = "http://127.0.0.1:8000"

st.title("🇮🇳 AI Finance Assistant — India Focused")
st.write("Institutional-grade company fundamental analysis powered by AI.")


# ====================== USER INPUT ======================
with st.container():
    st.subheader("🔍 Company Analyzer (NSE)")
    company = st.text_input(
        "Enter NSE stock symbol",
        placeholder="Example: RELIANCE / TCS / HDFCBANK / INFY / ICICIBANK"
    )

    analyze = st.button("Analyze Company", type="primary")


# ====================== PROCESS ======================
if analyze:
    if not company:
        st.warning("Enter a symbol first")
    else:
        symbol = company.upper()

        st.info(f"Fetching analysis for: **{symbol}** ...")

        try:
            res = requests.get(f"{BACKEND_URL}/company/{symbol}", timeout=25)

            if res.status_code != 200:
                st.error("Backend returned an error")
            else:
                data = res.json()

                if "error" in data:
                    st.error(data["error"])
                else:

                    st.success("Analysis Complete")

                    # ========== HEADER SUMMARY ==========
                    st.markdown("### 🧠 Analyst Headline View")
                    st.write(data["analyst_summary"]["headline_view"])
                    st.write("---")

                    # ========== MAIN GRID ==========
                    col1, col2 = st.columns(2)

                    # LEFT — BUSINESS / GROWTH / CASHFLOW
                    with col1:
                        st.markdown("### 📈 Business & Growth")

                        st.write("**Business Quality:**")
                        st.info(data["analyst_summary"]["business_quality_view"])

                        st.write("**Growth View:**")
                        st.info(data["analyst_summary"]["growth_view"])

                        st.write("**Cashflow Quality:**")
                        st.info(data["analyst_summary"]["cashflow_view"])

                    # RIGHT — FINANCIAL STRENGTH / VALUATION / RISK
                    with col2:
                        st.markdown("### 🛡️ Financial Strength & Risk")

                        st.write("**Financial Stability:**")
                        st.info(data["analyst_summary"]["financial_strength_view"])

                        st.write("**Valuation View:**")
                        st.info(data["analyst_summary"]["valuation_view"])

                        st.write("**Risk Flags:**")
                        for r in data["analyst_summary"]["risk_flags"]:
                            st.warning(f"- {r}")

                    st.write("---")

                    # ========== FINAL OPINION ==========
                    st.markdown("### 🧾 Final Investment Opinion")
                    st.success(data["analyst_summary"]["final_opinion"])

                    st.write("---")

                    # ========== RAW FUNDAMENTAL BLOCKS ==========
                    with st.expander("See Detailed Fundamental Data"):
                        st.json(data)

        except Exception as e:
            st.error("Could not connect to backend")
            st.write(e)
