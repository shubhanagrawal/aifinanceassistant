from fastapi import FastAPI
from src.utils.logger import get_logger
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

logger = get_logger("api")
app = FastAPI(title="AI Finance Research Assistant API")

@app.get("/health")
async def health_check():
    logger.info("Health check triggered")
    return {
        "status": "healthy",
        "service": "AI Finance Research Assistant API"
    }
