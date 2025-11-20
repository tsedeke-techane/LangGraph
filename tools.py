from langchain_core.tools import tool
from langgraph.types import interrupt
from datetime import datetime
import time
from functools import wraps  # ✅ import wraps


# ✅ Reuse the tracker with docstring preservation
def track_node(node_name):
    def decorator(func):
        @wraps(func)  # ✅ this keeps the original name & docstring
        def wrapper(*args, **kwargs):
            print(f"🟢 [{datetime.now().strftime('%H:%M:%S')}] ENTER TOOL: {node_name}")
            start_time = time.time()

            result = func(*args, **kwargs)

            elapsed = time.time() - start_time
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] EXIT TOOL: {node_name} ({elapsed:.2f}s)")
            return result
        return wrapper
    return decorator


@tool
@track_node("get_weather")
def get_weather(location: str) -> str:
    """Get current weather information for a location.
    :param location: City name or location
    :return: Weather information
    """
    # Mock weather data - in real implementation, you'd call a weather API
    weather_data = {
        "New York": "Sunny, 72°F, Humidity: 45%",
        "London": "Cloudy, 15°C, Humidity: 70%",
        "Tokyo": "Rainy, 20°C, Humidity: 85%",
        "Paris": "Partly cloudy, 18°C, Humidity: 55%",
        "Sydney": "Clear, 25°C, Humidity: 40%"
    }
    return weather_data.get(location, f"Weather data not available for {location}. Try major cities like New York, London, Tokyo, Paris, or Sydney.")


@tool
@track_node("get_stock_price")
def get_stock_price(symbol: str) -> str:
    """Get current stock price for a given symbol.
    :param symbol: Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)
    :return: Stock price information
    """
    stock_data = {
        "AAPL": "$175.50 (+2.3%)",
        "MSFT": "$380.25 (+1.8%)",
        "GOOGL": "$142.80 (+0.5%)",
        "AMZN": "$155.30 (-0.7%)",
        "TSLA": "$248.90 (+3.2%)"
    }
    return stock_data.get(symbol.upper(), f"Stock data not available for {symbol}. Try AAPL, MSFT, GOOGL, AMZN, or TSLA.")


@tool
@track_node("get_news_headlines")
def get_news_headlines(category: str = "general") -> str:
    """Get latest news headlines for a category.
    :param category: News category (technology, business, sports, entertainment, health)
    :return: News headlines
    """
    news_data = {
        "technology": [
            "AI Breakthrough: New Model Achieves Human-Level Reasoning",
            "Quantum Computing Milestone Reached by Tech Giant",
            "SpaceX Successfully Launches Latest Satellite Constellation"
        ],
        "business": [
            "Stock Market Hits All-Time High Amid Economic Recovery",
            "Cryptocurrency Market Shows Signs of Stabilization",
            "Major Merger Announced Between Tech Companies"
        ],
        "sports": [
            "Championship Game Ends in Dramatic Overtime Victory",
            "Star Athlete Signs Record-Breaking Contract",
            "Olympic Committee Announces Host City for 2032 Games"
        ]
    }

    headlines = news_data.get(category.lower(), [
        "Global Climate Summit Reaches Historic Agreement",
        "Medical Breakthrough Offers Hope for Rare Disease",
        "International Space Station Celebrates 25 Years"
    ])

    return f"📰 Latest {category.title()} News:\n" + "\n".join(f"• {headline}" for headline in headlines)


@tool
@track_node("suggest_recipe")
def suggest_recipe(ingredients: str, cuisine: str = "any") -> str:
    """Suggest a recipe based on available ingredients and cuisine preference.
    :param ingredients: Comma-separated list of available ingredients
    :param cuisine: Preferred cuisine type (italian, mexican, asian, american, etc.)
    :return: Recipe suggestion
    """
    ingredient_list = [ing.strip().lower() for ing in ingredients.split(",")]

    # Simple recipe matching logic
    if "chicken" in ingredient_list and "rice" in ingredient_list:
        return """
🍗 Chicken Fried Rice Recipe:
Ingredients: Chicken, rice, vegetables, soy sauce, eggs
Instructions:
1. Cook rice and set aside
2. Stir-fry chicken until cooked
3. Add vegetables and scrambled eggs
4. Mix in rice and soy sauce
5. Serve hot
Time: 25 minutes | Serves: 4
"""
    elif "pasta" in ingredient_list and "tomato" in ingredient_list:
        return """
🍝 Simple Pasta Sauce Recipe:
Ingredients: Pasta, tomatoes, garlic, olive oil, basil
Instructions:
1. Cook pasta according to package
2. Sauté garlic in olive oil
3. Add chopped tomatoes and simmer
4. Season with basil and salt
5. Toss with cooked pasta
Time: 20 minutes | Serves: 2
"""
    else:
        return f"""
🍳 Custom Recipe Suggestion:
Based on your ingredients: {ingredients}
For {cuisine} cuisine, I recommend:

Ingredients you'll need: {ingredients}, plus basic pantry items
Suggested dish: Stir-fried medley with your available ingredients

Quick Instructions:
1. Prep all ingredients (chop, measure)
2. Heat oil in a pan or wok
3. Cook proteins first (if any)
4. Add vegetables and aromatics
5. Season and finish cooking
6. Serve immediately

Pro tip: Start with the longest-cooking ingredients first!
"""


@tool
@track_node("convert_units")
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between different units of measurement.
    :param value: Numeric value to convert
    :param from_unit: Source unit (kg, lbs, celsius, fahrenheit, meters, feet, etc.)
    :param to_unit: Target unit
    :return: Converted value
    """
    conversions = {
        ("kg", "lbs"): lambda x: x * 2.20462,
        ("lbs", "kg"): lambda x: x / 2.20462,
        ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        ("meters", "feet"): lambda x: x * 3.28084,
        ("feet", "meters"): lambda x: x / 3.28084,
        ("km", "miles"): lambda x: x * 0.621371,
        ("miles", "km"): lambda x: x / 0.621371,
        ("liters", "gallons"): lambda x: x * 0.264172,
        ("gallons", "liters"): lambda x: x / 0.264172
    }

    key = (from_unit.lower(), to_unit.lower())
    if key in conversions:
        result = conversions[key](value)
        return ".2f"
    else:
        return f"❌ Conversion from {from_unit} to {to_unit} not supported. Try: kg↔lbs, celsius↔fahrenheit, meters↔feet, km↔miles, liters↔gallons."


tools = [get_weather, get_stock_price, get_news_headlines, suggest_recipe, convert_units]