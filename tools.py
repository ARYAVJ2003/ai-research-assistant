from langchain.tools import tool

@tool
def web_search(query: str) -> str:
    """Search the web for latest or factual information"""
    return f"""Search result for '{query}'"""


@tool
def calculator(expression: str) -> str:
    """Calculate mathematical expressions"""

    try:
        return str(eval(expression))
    except:
        return "Invalid expression"