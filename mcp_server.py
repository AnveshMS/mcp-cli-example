#!/usr/bin/env python3
"""
MCP Server for Simple Calculator - Uses stdio protocol
This allows mcp-cli to communicate with the server via standard input/output
"""

import json
import sys
from tools import TOOLS


def build_tool_schema(name: str, tool_info: dict) -> dict:
    """Convert tool info to MCP-compliant tool schema"""
    params = tool_info.get("parameters", {})
    properties = {}
    required = []

    for param_name, param_type in params.items():
        properties[param_name] = {
            "type": "number" if param_type == "float" else param_type.lower()
        }
        required.append(param_name)

    return {
        "name": name,
        "description": tool_info.get("description", ""),
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required
        }
    }


def handle_initialize(request_id):
    """Handle initialization request"""
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "Simple Calculator MCP Server",
                "version": "1.0.0"
            }
        }
    }
    return response


def handle_list_tools(request_id):
    """Handle list tools request"""
    tools = []
    for name, tool_info in TOOLS.items():
        tools.append(build_tool_schema(name, tool_info))
    
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": tools
        }
    }
    return response


def handle_call_tool(request_id, params):
    """Handle tool call request"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    if not tool_name or tool_name not in TOOLS:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Tool '{tool_name}' not found"
            }
        }

    try:
        tool_function = TOOLS[tool_name]["function"]
        result = tool_function(**arguments)

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result)
                    }
                ]
            }
        }
    except TypeError as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": f"Invalid parameters: {str(e)}"
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": f"Error executing tool: {str(e)}"
            }
        }


def main():
    """Main loop - read from stdin, process, write to stdout"""
    while True:
        try:
            # Read a line from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            # Parse JSON
            request = json.loads(line.strip())
            method = request.get("method")
            request_id = request.get("id")
            params = request.get("params", {})

            # Route to appropriate handler
            if method == "initialize":
                response = handle_initialize(request_id)
            elif method == "tools/list":
                response = handle_list_tools(request_id)
            elif method == "tools/call":
                response = handle_call_tool(request_id, params)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }

            # Write response
            print(json.dumps(response))
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
