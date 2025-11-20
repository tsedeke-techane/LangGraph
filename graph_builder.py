from typing import Annotated, TypedDict, Literal
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import time
from datetime import datetime
import re

from tools import tools
from config import MODEL_NAME

class State(TypedDict):
    messages: Annotated[list, add_messages]

# Execution tracking decorator
def track_node(node_name):
    def decorator(func):
        def wrapper(state: State):
            print(f"🟢 [{datetime.now().strftime('%H:%M:%S')}] ENTER: {node_name}")
            start_time = time.time()

            result = func(state)

            elapsed = time.time() - start_time
            print(f"✅ [{datetime.now().strftime('%H:%M:%S')}] EXIT: {node_name} ({elapsed:.2f}s)")
            return result
        return wrapper
    return decorator

def route_to_tool(user_input: str) -> str:
    """Simple rule-based routing to determine which tool to use based on user input"""
    input_lower = user_input.lower()

    # Weather patterns
    if any(word in input_lower for word in ['weather', 'temperature', 'forecast']):
        # Extract location
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

    # Default fallback - use weather
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
    

    
def create_graph():
    try:
        llm = init_chat_model(MODEL_NAME)
        llm_with_tools = llm.bind_tools(tools)
        use_demo_mode = False
    except Exception as e:
        print(f"⚠️ API Error: {e}\n🔄 Demo Mode enabled")
        llm_with_tools = None
        use_demo_mode = True

    def call_llm(messages):
        return {"messages": [llm.invoke(messages)]}

    @track_node("draft_agent")
    def draft_node(state: State) -> State:
        if use_demo_mode:
            user_input = state["messages"][-1].content
            return {"messages": [HumanMessage(content=demo_agent_response(user_input))]}
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    @track_node("critique_agent")
    def critique_node(state: State) -> State:
        if use_demo_mode:
            return {"messages": state["messages"] + [HumanMessage(content="APPROVE")]}
        msgs = state["messages"] + [HumanMessage(content="Review the text above. If under 50 words or lacking detail respond 'REVISE', else 'APPROVE'.")]
        return call_llm(msgs)

    @track_node("refine_agent")
    def refine_node(state: State) -> State:
        if use_demo_mode:
            return state
        msgs = state["messages"] + [HumanMessage(content="Improve and expand while keeping core message.")]
        return call_llm(msgs)

    @track_node("seo_agent")
    def seo_node(state: State) -> State:
        if use_demo_mode:
            return {"messages": state["messages"] + [HumanMessage(content="Keywords: AI, assistant, tools, demo")]}
        msgs = state["messages"] + [HumanMessage(content="Extract 5-7 SEO keywords, comma-separated.")]
        return call_llm(msgs)

    @track_node("summary_agent")
    def summary_node(state: State) -> State:
        if use_demo_mode:
            return state
        msgs = state["messages"] + [HumanMessage(content="Write a concise 2-sentence SEO meta description.")]
        return call_llm(msgs)

    def should_refine(state: State) -> Literal["refine_agent", "seo_agent"]:
        content = state["messages"][-1].content.upper()
        return "refine_agent" if "REVISE" in content else "seo_agent"

    builder = StateGraph(State)
    builder.add_node("draft_agent", draft_node)
    builder.add_node("critique_agent", critique_node)
    builder.add_node("refine_agent", refine_node)
    builder.add_node("seo_agent", seo_node)
    builder.add_node("summary_agent", summary_node)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "draft_agent")

    if use_demo_mode:
        builder.add_edge("draft_agent", END)
    else:
        builder.add_conditional_edges("draft_agent", tools_condition, {"tools": "tools", "__end__": "critique_agent"})
        builder.add_edge("tools", "draft_agent")
        builder.add_conditional_edges("critique_agent", should_refine)
        builder.add_edge("refine_agent", "seo_agent")
        builder.add_edge("seo_agent", "summary_agent")
        builder.add_edge("summary_agent", END)

    conn = sqlite3.connect("graph_state.db", check_same_thread=False)
    memory = SqliteSaver(conn)
    return builder.compile(checkpointer=memory)

graph = create_graph()
