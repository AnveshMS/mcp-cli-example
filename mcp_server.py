#!/usr/bin/env python3
"""
MCP Server for Simple Calculator - Uses stdio protocol
This allows mcp-cli to communicate with the server via standard input/output
"""

import json
import sys
import logging
from datetime import datetime
from tools import TOOLS

# Configure logging to stderr (so it doesn't interfere with JSON-RPC on stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MCP-SERVER] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)


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
    logger.info("🔧 INITIALIZE request received")
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
    logger.info(f"✓ Initialized: {response['result']['serverInfo']['name']}")
    return response


def handle_list_tools(request_id):
    """Handle list tools request"""
    logger.info("📋 LIST TOOLS request received")
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
    logger.info(f"✓ Returning {len(tools)} tools: {[t['name'] for t in tools]}")
    return response


def handle_call_tool(request_id, params):
    """Handle tool call request"""
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    logger.info(f"🔨 CALL TOOL request received")
    logger.info(f"   Tool: {tool_name}")
    logger.info(f"   Arguments: {arguments}")

    if not tool_name or tool_name not in TOOLS:
        logger.error(f"✗ Tool '{tool_name}' not found")
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
        logger.info(f"✓ Tool executed successfully: {result}")

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
        logger.error(f"✗ Invalid parameters: {str(e)}")
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32602,
                "message": f"Invalid parameters: {str(e)}"
            }
        }
    except Exception as e:
        logger.error(f"✗ Error executing tool: {str(e)}")
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
    logger.info("=" * 60)
    logger.info("🚀 MCP SERVER STARTED (stdio mode)")
    logger.info("   Waiting for JSON-RPC requests via stdin...")
    logger.info("   (Can be called by mcp-cli OR directly)")
    logger.info("=" * 60)
    
    while True:
        try:
            # Read a line from stdin
            line = sys.stdin.readline()
            if not line:
                logger.info("📴 No more input - shutting down")
                break
            
            # Parse JSON
            request = json.loads(line.strip())
            method = request.get("method")
            request_id = request.get("id")
            params = request.get("params", {})
            
            logger.info(f"\n📥 Received request: method='{method}', id={request_id}")

            # Route to appropriate handler
            if method == "initialize":
                response = handle_initialize(request_id)
            elif method == "tools/list":
                response = handle_list_tools(request_id)
            elif method == "tools/call":
                response = handle_call_tool(request_id, params)
            else:
                logger.warning(f"⚠️  Unknown method: {method}")
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
            logger.error(f"✗ JSON Parse error: {str(e)}")
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
            logger.error(f"✗ Internal error: {str(e)}")
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
