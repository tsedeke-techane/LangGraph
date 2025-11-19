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
@track_node("summarize_text")
def summarize_text(text: str) -> str:
    """Summarize a given text."""
    return text[:100] + "..." if len(text) > 100 else text


@tool
@track_node("write_MMS_format")
def write_MMS_format(text: str) -> str:
    """Use this tool to write an essay in MMS format."""
    words = text.split()
    keywords = [word for i, word in enumerate(words) if i % 3 == 0]  # simple example
    return ", ".join(keywords)


@tool
@track_node("save_or_publish")
def save_or_publish(content: str) -> str:
    """Use this tool whenever the user wants to save or publish any content.
    Always ask for human approval before finalizing."""
    decision = interrupt(f"Approve saving the content?\n{content}")
    if decision.lower() == "yes":
        return "Content saved successfully!"
    return "saving declined."


tools = [summarize_text, write_MMS_format, save_or_publish]
