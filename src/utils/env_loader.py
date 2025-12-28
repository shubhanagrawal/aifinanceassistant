from dotenv import load_dotenv
import os

load_dotenv()

def get_env(name: str, default=None, required: bool = False):
    value = os.getenv(name, default)

    if required and (value is None or value == ""):
        raise ValueError(f"Missing required environment variable: {name}")

    return value

APP_ENV = get_env("APP_ENV", "dev")
LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
