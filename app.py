from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from tools import TOOLS

app = FastAPI(title="Simple MCP Server")


# ============================================================================
# LEGACY ENDPOINTS (Backward Compatibility)
# ============================================================================

# Request model (AI sends this)
class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict = {}


# Endpoint 1: List available tools
@app.get("/tools")
def list_tools():
    tool_list = []
    for name, tool in TOOLS.items():
        tool_list.append({
            "name": name,
            "description": tool["description"],
            "parameters": tool["parameters"]
        })
    return {"tools": tool_list}


# Endpoint 2: Execute a tool
@app.post("/execute")
def execute_tool(request: ToolRequest):
    if request.tool_name not in TOOLS:
        raise HTTPException(status_code=404, detail="Tool not found")

    tool = TOOLS[request.tool_name]["function"]

    try:
        result = tool(**request.arguments)
        return {
            "tool": request.tool_name,
            "output": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MCP PROTOCOL ENDPOINTS (JSON-RPC 2.0 Compliant)
# ============================================================================

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: str
    params: Dict[str, Any] = {}


class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None


def build_tool_schema(name: str, tool_info: Dict) -> Dict[str, Any]:
    """Convert tool info to MCP-compliant tool schema"""
    # Extract parameter information
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


@app.post("/mcp/initialize")
def mcp_initialize(request: MCPRequest) -> MCPResponse:
    """MCP Initialize method - establish connection"""
    return MCPResponse(
        jsonrpc="2.0",
        id=request.id,
        result={
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "Simple Calculator MCP Server",
                "version": "1.0.0"
            }
        }
    )


@app.post("/mcp/tools/list")
def mcp_list_tools(request: MCPRequest) -> MCPResponse:
    """MCP tools/list method - list all available tools"""
    tools = []
    for name, tool_info in TOOLS.items():
        tools.append(build_tool_schema(name, tool_info))

    return MCPResponse(
        jsonrpc="2.0",
        id=request.id,
        result={"tools": tools}
    )


@app.post("/mcp/tools/call")
def mcp_call_tool(request: MCPRequest) -> MCPResponse:
    """MCP tools/call method - execute a tool"""
    try:
        params = request.params
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if not tool_name or tool_name not in TOOLS:
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Tool '{tool_name}' not found"
                }
            )

        tool_function = TOOLS[tool_name]["function"]
        result = tool_function(**arguments)

        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            result={
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }
        )

    except TypeError as e:
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            error={
                "code": -32602,
                "message": f"Invalid parameters: {str(e)}"
            }
        )
    except Exception as e:
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            error={
                "code": -32603,
                "message": f"Error executing tool: {str(e)}"
            }
        )


@app.get("/mcp")
def mcp_root():
    """MCP root endpoint - server info"""
    return {
        "name": "Simple Calculator MCP Server",
        "version": "1.0.0",
        "description": "A simple MCP server with calculator tools",
        "endpoints": {
            "initialize": "POST /mcp/initialize",
            "list_tools": "POST /mcp/tools/list",
            "call_tool": "POST /mcp/tools/call"
        }
    }


@app.post("/mcp")
def mcp_router(request: MCPRequest) -> MCPResponse:
    """Route MCP requests to appropriate handlers"""
    method = request.method
    
    if method == "initialize":
        return mcp_initialize(request)
    elif method == "tools/list":
        return mcp_list_tools(request)
    elif method == "tools/call":
        return mcp_call_tool(request)
    else:
        return MCPResponse(
            jsonrpc="2.0",
            id=request.id,
            error={
                "code": -32601,
                "message": f"Method '{method}' not found"
            }
        )
