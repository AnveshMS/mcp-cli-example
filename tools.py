from datetime import datetime

# Tool 1: Calculator
def add_numbers(a: float, b: float):
    return {"result": a + b}

def subtract_numbers(a: float, b: float):
    return {"result": a - b}

def divide_numbers(a: float, b: float):
    if b == 0:
        return {"error": "Cannot divide by zero"}
    return {"result": a / b}

# Tool 3: Current Time
def get_current_time():
    return {"current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# Tool registry (important for MCP style)
TOOLS = {
    "add_numbers": {
        "function": add_numbers,
        "description": "Add two numbers",
        "parameters": {
            "a": "float",
            "b": "float"
        }
    },
    "subtract_numbers": {
        "function": subtract_numbers,
        "description": "Subtract two numbers",
        "parameters": {
            "a": "float",
            "b": "float"
        }
    },
    "divide_numbers": {
        "function": divide_numbers,
        "description": "Divide two numbers",
        "parameters": {
            "a": "float",
            "b": "float"
        }
    },
    "get_current_time": {
        "function": get_current_time,
        "description": "Get current system time",
        "parameters": {}
    }
}
