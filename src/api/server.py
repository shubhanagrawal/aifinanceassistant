from fastapi import FastAPI
from src.utils.logger import get_logger
import sys
import os
from engines.market_context import get_market_context

from fastapi import APIRouter
from engines.company_engine import build_company_analysis


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

router = APIRouter()

logger = get_logger("api")
app = FastAPI(title="AI Finance Research Assistant API")

@app.get("/health")
async def health_check():
    logger.info("Health check triggered")
    return {
        "status": "healthy",
        "service": "AI Finance Research Assistant API"
    }

from engines.market_context import get_market_context

@app.get("/market/context")
async def market_context():
    return get_market_context()

@router.get("/company/{symbol}")
async def get_company(symbol: str):
    result = build_company_analysis(symbol)

    if not result:
        return {"error": "Failed to fetch company data"}

    return result





@app.get("/company/{symbol}")
async def company_analysis(symbol: str):
    try:
        result = build_company_analysis(symbol.upper())

        if not result:
            return {"error": "Could not fetch data. Possibly invalid symbol."}

        return result

    except Exception as e:
        return {"error": str(e)}


