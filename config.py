import os
from dotenv import load_dotenv

load_dotenv()

try:
    from .tools import (
        MODEL_NAME as DEFAULT_MODEL_NAME,
        DEMO_MODE as DEFAULT_DEMO_MODE,
        get_weather,
        get_stock_price,
        get_news_headlines,
        suggest_recipe,
        convert_units,
    )
except Exception:
    DEFAULT_MODEL_NAME = "demo"
    DEFAULT_DEMO_MODE = True
    # Dummy fallbacks so list still builds
    def _na(*a, **k): raise RuntimeError("Tool unavailable")
    get_weather = get_stock_price = get_news_headlines = suggest_recipe = convert_units = _na

MODEL_NAME = DEFAULT_MODEL_NAME
DEMO_MODE = DEFAULT_DEMO_MODE

TOOLS = [
    get_weather,
    get_stock_price,
    get_news_headlines,
    suggest_recipe,
    convert_units,
]

def tools_functional():
    try:
        return all(callable(t) for t in TOOLS)
    except Exception:
        return False

# If tools not functional, prefer Gemini when credentials exist
if (os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")) and not tools_functional():
    MODEL_NAME = "google_genai:gemini-2.0-flash"
    DEMO_MODE = False