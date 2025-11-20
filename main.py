from tools import tools
from datetime import datetime
import time
import re

def route_to_tool(user_input: str) -> str:
    """Simple rule-based routing to determine which tool to use based on user input"""
    input_lower = user_input.lower()

    # Weather patterns
    if any(word in input_lower for word in ['weather', 'temperature', 'forecast']):
        locations = ['new york', 'london', 'tokyo', 'paris', 'sydney']
        for location in locations:
            if location in input_lower:
                return f"get_weather:{location}"
        return "get_weather:new york"  # default

    # Stock patterns
    elif any(word in input_lower for word in ['stock', 'price', 'aapl', 'apple', 'msft', 'microsoft', 'googl', 'google', 'amzn', 'amazon', 'tsla', 'tesla']):
        symbols = {'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL', 'amazon': 'AMZN', 'tesla': 'TSLA'}
        for company, symbol in symbols.items():
            if company in input_lower or symbol.lower() in input_lower:
                return f"get_stock_price:{symbol}"
        return "get_stock_price:AAPL"  # default

    # News patterns
    elif any(word in input_lower for word in ['news', 'headlines', 'latest']):
        categories = ['technology', 'business', 'sports', 'entertainment', 'health']
        for category in categories:
            if category in input_lower:
                return f"get_news_headlines:{category}"
        return "get_news_headlines:general"

    # Recipe patterns
    elif any(word in input_lower for word in ['recipe', 'cook', 'make', 'ingredients']):
        return f"suggest_recipe:{user_input}"

    # Unit conversion patterns
    elif any(word in input_lower for word in ['convert', 'to ', 'from ']):
        return f"convert_units:{user_input}"

    # Default fallback
    return f"get_weather:new york"

def demo_agent_response(user_input: str) -> str:
    """Generate a demo response by directly calling the appropriate tool"""
    try:
        route = route_to_tool(user_input)
        tool_name, *args = route.split(':')

        # Find the tool
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return f"❌ Tool '{tool_name}' not found. Available tools: {[t.name for t in tools]}"

        # Call the tool with appropriate arguments
        if tool_name == 'get_weather':
            result = tool.invoke(args[0] if args else 'New York')
        elif tool_name == 'get_stock_price':
            result = tool.invoke(args[0] if args else 'AAPL')
        elif tool_name == 'get_news_headlines':
            result = tool.invoke(args[0] if args else 'general')
        elif tool_name == 'suggest_recipe':
            result = tool.invoke(args[0] if args else 'chicken, rice')
        elif tool_name == 'convert_units':
            # Parse conversion request - for now use default
            result = tool.invoke(10.0, 'kg', 'lbs')
        else:
            result = f"🤖 Demo Mode: I understood you want to use the {tool_name} tool, but I'm not sure how to call it with: {args}"

        return result

    except Exception as e:
        return f"❌ Error in demo mode: {str(e)}"

def main():
    print("🤖 AI Tool Assistant (Demo Mode)")
    print("📊 Available Tools:")
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")
    print("=" * 50)

    session_stats = []

    while True:
        user_input = input("\n💬 You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print(f"\n📈 Session Summary - {len(session_stats)} requests:")
            for i, stat in enumerate(session_stats, 1):
                print(f"  {i}. {stat}")
            print("👋 Goodbye!")
            break

        if not user_input:
            print("⚠️  Please enter a message")
            continue

        # Track execution
        print(f"\n🚀 Processing at {datetime.now().strftime('%H:%M:%S')}")
        start_time = time.time()

        try:
            response = demo_agent_response(user_input)
            elapsed = time.time() - start_time

            print(f"\n🤖 Bot: {response}")
            print("=" * 40)
            print(f"📊 Processed in: {elapsed:.2f}s")

            # Store session stats
            session_stats.append(f"{elapsed:.2f}s - '{user_input[:20]}...'")

        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ Error after {elapsed:.2f}s: {e}")

if __name__ == "__main__":
    main()