import streamlit as st
from utils.env_loader import get_env, APP_ENV
from utils.logger import get_logger
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)


logger = get_logger("ui")

st.set_page_config(page_title="AI Finance Research Assistant", layout="centered")

st.title("AI Finance Research Assistant")
st.success("Frontend is running successfully 🚀")
st.info(f"Environment: {APP_ENV}")

logger.info("Streamlit UI loaded successfully")
