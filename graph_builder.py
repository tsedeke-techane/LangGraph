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

def create_graph():
    llm = init_chat_model(MODEL_NAME)
    llm_with_tools = llm.bind_tools(tools)
    
    @track_node("draft_agent")
    def draft_node(state: State) -> State:
        """Node 1: Generate initial content."""
        # The first node simply processes the user's request
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    @track_node("critique_agent")
    def critique_node(state: State) -> State:
        """Node 2: Review the content quality."""
        # We ask the LLM to review the previous message
        messages = state["messages"] + [
            HumanMessage(content="Review the text above. If it is too short (under 50 words) or lacks detail, respond with 'REVISE'. Otherwise, respond with 'APPROVE'.")
        ]
        return {"messages": [llm.invoke(messages)]}

    @track_node("refine_agent") 
    def refine_node(state: State) -> State:
        """Node 3: Improve content if needed."""
        messages = state["messages"] + [
            HumanMessage(content="Please rewrite the article to be more detailed and comprehensive based on the critique.")
        ]
        return {"messages": [llm.invoke(messages)]}

    @track_node("seo_agent")
    def seo_node(state: State) -> State:
        """Node 4: Extract keywords."""
        messages = state["messages"] + [
            HumanMessage(content="Extract top 5 SEO keywords from the article. Format: 'Keywords: ...'")
        ]
        return {"messages": [llm.invoke(messages)]}
    
    @track_node("summary_agent")
    def summary_node(state: State) -> State:
        """Node 5: Create a meta description."""
        messages = state["messages"] + [
            HumanMessage(content="Write a 2-sentence meta description for this article.")
        ]
        return {"messages": [llm.invoke(messages)]}

    # Conditional Logic for Routing
    def should_refine(state: State) -> Literal["refine_agent", "seo_agent"]:
        last_message = state["messages"][-1]
        content = last_message.content.upper()
        if "REVISE" in content:
            print("🔀 Decision: Content needs refinement.")
            return "refine_agent"
        print("🔀 Decision: Content approved.")
        return "seo_agent"

    builder = StateGraph(State)

    # Add nodes
    builder.add_node("draft_agent", draft_node)
    builder.add_node("critique_agent", critique_node)
    builder.add_node("refine_agent", refine_node)
    builder.add_node("seo_agent", seo_node)
    builder.add_node("summary_agent", summary_node)
    builder.add_node("tools", ToolNode(tools))

    # Edges
    builder.add_edge(START, "draft_agent")
    
    # Draft -> Tools check. 
    # If tools used, go to tools. 
    # If done (no tools), go to critique.
    builder.add_conditional_edges(
        "draft_agent", 
        tools_condition, 
        {"tools": "tools", "__end__": "critique_agent"}
    )
    builder.add_edge("tools", "draft_agent")

    # Critique -> Refine OR SEO (Branching Logic)
    builder.add_conditional_edges("critique_agent", should_refine)

    # Refine -> SEO
    builder.add_edge("refine_agent", "seo_agent")
    
    # SEO -> Summary
    builder.add_edge("seo_agent", "summary_agent")
    
    # Summary -> End
    builder.add_edge("summary_agent", END)
    
    conn = sqlite3.connect("graph_state.db", check_same_thread=False)
    memory = SqliteSaver(conn)

    return builder.compile(checkpointer=memory)

graph = create_graph()
