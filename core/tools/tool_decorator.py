from functools import wraps
from typing import Any, Callable
from smolagents import tool

def azure_tool(func: Callable) -> Callable:
    """
    Decorator that combines smolagents tool with Azure-specific error handling.
    
    Args:
        func: The function to decorate
    """
    @tool  # Use smolagents tool decorator
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed",
                "function": func.__name__
            }
    return wrapper
