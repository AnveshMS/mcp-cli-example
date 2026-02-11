# Simple MCP Calculator Server

A complete MCP (Model Context Protocol) server implementation that exposes calculator tools through the `mcp-cli` command-line interface and FastAPI HTTP endpoints.

✅ **Working Status:** Fully functional and tested with mcp-cli

## Quick Start (30 seconds)

```bash
# 1. Install mcp-cli locally (one-time setup)
bun install mcp-cli@github:philschmid/mcp-cli

# 2. List available tools
.\node_modules\.bin\mcp-cli -c mcp_servers.json

# 3. Call a tool
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}'

# Output: {"result": 8}
```

Done! No server process needed. mcp-cli communicates directly with the MCP server via Python stdio protocol.

## Features

✅ **MCP CLI Compatible** - Works with `mcp-cli` for dynamic tool discovery  
✅ **Backward Compatible** - Legacy endpoints still available  
✅ **Full Tool Schema** - MCP-compliant inputSchema for each tool  
✅ **JSON-RPC 2.0** - Standard protocol for tool communication  
✅ **Easy Demo** - Simple commands to test functionality  

## Project Files

- **app.py** - FastAPI application (legacy HTTP endpoints + optional MCP HTTP endpoints)
- **tools.py** - Tool implementations and registry (shared by both servers)
- **mcp_server.py** - Stdio-based MCP server (recommended for mcp-cli)
- **mcp_servers.json** - Configuration for mcp-cli
- **requirements.txt** - Python dependencies
- **package.json** / **bun.lockb** - Node.js dependencies (created by bun/npm)
- **node_modules/** - Installed packages (including mcp-cli)

## Installation

### Prerequisites
- Python 3.8+
- Node.js/npm (for mcp-cli)
- Bun (optional, recommended for mcp-cli)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation

### 2. Install mcp-cli (Local Installation)

The easiest way to install mcp-cli is locally in your project:

```bash
# Using bun (recommended)
bun install mcp-cli@github:philschmid/mcp-cli

# OR using npm
npm install mcp-cli@github:philschmid/mcp-cli
```

After installation, mcp-cli will be available at:
```bash
.\node_modules\.bin\mcp-cli   # Windows
./node_modules/.bin/mcp-cli    # Mac/Linux
```

**Verify Installation:**
```bash
.\node_modules\.bin\mcp-cli --version
```

### 3. Alternative: Global Installation

If you prefer global installation:

**Using Bun:**
```bash
bun install -g https://github.com/philschmid/mcp-cli
```

**Using npm:**
```bash
npm install -g https://github.com/philschmid/mcp-cli
```

Then use `mcp-cli` directly in your terminal.

## Running the Server

### Option 1: FastAPI Server (Optional - For Legacy HTTP Endpoints)

```bash
uvicorn app:app --reload
```

Server runs on: `http://localhost:8000`

The server will be available at:
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **MCP Endpoints**: `http://localhost:8000/mcp`

### Option 2: Using mcp-cli (Recommended)

No need to start a separate server! mcp-cli communicates directly with the `mcp_server.py` script via stdio protocol.

Just run mcp-cli commands directly:
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json
```

## Available Tools

### 1. add_numbers
Adds two numbers together.

**Parameters:**
- `a` (float): First number
- `b` (float): Second number

**Returns:** `{"result": sum}`

### 2. subtract_numbers
Subtracts the second number from the first.

**Parameters:**
- `a` (float): First number
- `b` (float): Second number

**Returns:** `{"result": difference}`

### 3. divide_numbers
Divides the first number by the second.

**Parameters:**
- `a` (float): Numerator
- `b` (float): Denominator

**Returns:** `{"result": quotient}`

**Note:** Returns error if dividing by zero.

### 4. get_current_time
Returns the current system time.

**Returns:** `{"current_time": "YYYY-MM-DD HH:MM:SS"}`

## Usage Examples

### Option 1: Legacy HTTP Endpoints

#### List Tools
```bash
curl http://localhost:8000/tools
```

#### Execute a Tool
```bash
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "add_numbers", "arguments": {"a": 3, "b": 2}}'
```

### Option 2: MCP CLI (Recommended for Demos)

#### 1. Discover Available Tools
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json
```

Output:
```
simple-calculator
  • add_numbers
  • subtract_numbers
  • divide_numbers
  • get_current_time
```

#### 2. View Tools with Descriptions
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json -d
```

#### 3. Inspect a Specific Tool
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json info simple-calculator add_numbers
```

Output:
```
Tool: add_numbers
Server: simple-calculator

Description:
  Add two numbers

Input Schema:
{
  "type": "object",
  "properties": {
    "a": {"type": "number"},
    "b": {"type": "number"}
  },
  "required": ["a", "b"]
}
```

#### 4. Execute a Tool
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 3, "b": 2}'
```

Output:
```
{"result": 5}
```

#### 5. Execute Multiple Tools
```bash
# Subtract
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator subtract_numbers '{"a": 10, "b": 3}'

# Divide
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator divide_numbers '{"a": 15, "b": 3}'

# Get current time
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator get_current_time '{}'
```

#### 6. Advanced: Chain Multiple Calls
```bash
# Execute add and parse result (requires jq)
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}' | jq '.result'
```

## MCP Protocol Endpoints

The server implements the following MCP JSON-RPC 2.0 endpoints:

### POST /mcp/initialize
Initializes the MCP connection and returns server capabilities.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
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
```

### POST /mcp/tools/list
Lists all available tools with their schemas.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "add_numbers",
        "description": "Add two numbers",
        "inputSchema": {
          "type": "object",
          "properties": {
            "a": {"type": "number"},
            "b": {"type": "number"}
          },
          "required": ["a", "b"]
        }
      },
      ...
    ]
  }
}
```

### POST /mcp/tools/call
Executes a tool and returns the result.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "add_numbers",
    "arguments": {
      "a": 3,
      "b": 2
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{'result': 5}"
      }
    ]
  }
}
```

### GET /mcp
Returns server information and available endpoints.

**Response:**
```json
{
  "name": "Simple Calculator MCP Server",
  "version": "1.0.0",
  "description": "A simple MCP server with calculator tools",
  "endpoints": {
    "initialize": "POST /mcp/initialize",
    "list_tools": "POST /mcp/tools/list",
    "call_tool": "POST /mcp/tools/call"
  }
}
```

## Demo Walkthrough

### Quick Start (3 Steps)

**Step 1: Install mcp-cli locally**
```bash
bun install mcp-cli@github:philschmid/mcp-cli
```

**Step 2: List available tools**
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json
```

**Step 3: Call a tool**
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}'
```

### Full Demo Sequence

```bash
# 1. Discover tools
.\node_modules\.bin\mcp-cli -c mcp_servers.json

# 2. View tool details
.\node_modules\.bin\mcp-cli -c mcp_servers.json -d

# 3. Get schema for specific tool
.\node_modules\.bin\mcp-cli -c mcp_servers.json info simple-calculator divide_numbers

# 4. Run demo calculations
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}'
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator subtract_numbers '{"a": 10, "b": 4}'
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator divide_numbers '{"a": 20, "b": 5}'
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator get_current_time '{}'

# 5. Test error handling (divide by zero)
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator divide_numbers '{"a": 10, "b": 0}'
```

## Configuration

### mcp_servers.json

The `mcp_servers.json` file configures mcp-cli to connect to your MCP server:

```json
{
  "mcpServers": {
    "simple-calculator": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

This configuration:
- Uses Python to run `mcp_server.py` (stdio-based MCP server)
- Communicates via standard input/output protocol
- Requires the config file to be in the current directory or `~/.config/mcp/`

**Optional: Tool Filtering**

You can restrict which tools are available:

```json
{
  "mcpServers": {
    "simple-calculator": {
      "command": "python",
      "args": ["mcp_server.py"],
      "allowedTools": ["add_numbers", "divide_numbers"],
      "disabledTools": ["get_current_time"]
    }
  }
}
```

- `allowedTools`: Only these tools are available (supports glob patterns like `*numbers`)
- `disabledTools`: These tools are disabled (takes precedence over allowedTools)

## Troubleshooting

### mcp-cli command not found
```bash
# If using local installation, use the full path
.\node_modules\.bin\mcp-cli --version   # Windows
./node_modules/.bin/mcp-cli --version    # Mac/Linux

# OR install globally
bun install -g https://github.com/philschmid/mcp-cli
```

### Config file not found
- Ensure `mcp_servers.json` is in your current working directory
- Or place it in `~/.config/mcp/mcp_servers.json`
- Verify the path with `-c mcp_servers.json` flag

### Tool execution fails
- Check tool parameters match expected types (floats for calculator tools)
- Verify JSON syntax in arguments
- For divide_numbers, ensure denominator is not zero

### Python module not found
```bash
# Ensure tools.py is in the same directory as mcp_server.py
# Test by running:
python -c "from tools import TOOLS; print(list(TOOLS.keys()))"
```

### Port already in use (If using FastAPI server)
```bash
# If port 8000 is in use, specify a different port
uvicorn app:app --reload --port 8001
```

## Architecture

### Stdio-Based MCP Server Flow
```
mcp-cli
  ↓
stdin → mcp_server.py (JSON-RPC 2.0 protocol)
  ↓
stdout → Result
```

**How it works:**
1. mcp-cli executes `python mcp_server.py`
2. Sends JSON-RPC requests via stdin
3. mcp_server.py processes requests (initialize, list tools, call tools)
4. Returns JSON-RPC responses via stdout
5. mcp-cli parses and displays results

### Legacy HTTP Flow (Optional - For Reference)
```
FastAPI Server (app.py)
  ↓
GET/POST /tools        → List tools (legacy)
GET/POST /execute      → Execute tool (legacy)
GET/POST /mcp/*        → MCP protocol endpoints
```

Both approaches work independently. The stdio-based approach (via mcp_server.py) is recommended for mcp-cli integration.

## API Documentation

Interactive API documentation is available at: `http://localhost:8000/docs`

This provides a Swagger UI interface to test all endpoints including both legacy HTTP and MCP endpoints.

## Development

### Adding New Tools

1. **Define the tool function in `tools.py`:**
   ```python
   def multiply_numbers(a: float, b: float):
       return {"result": a * b}
   ```

2. **Register in TOOLS dictionary:**
   ```python
   TOOLS = {
       ...
       "multiply_numbers": {
           "function": multiply_numbers,
           "description": "Multiply two numbers",
           "parameters": {
               "a": "float",
               "b": "float"
           }
       }
   }
   ```

3. **Restart the server** - no changes needed to `app.py`!

The MCP endpoints automatically discover and expose new tools.

## MCP Protocol Version

This server implements the **MCP Protocol 2024-11-05** specification.

For more information, visit: https://modelcontextprotocol.io/

## License

Open source - Feel free to use and modify for your projects.

## Support

For issues or questions:
- Check MCP CLI documentation: https://github.com/philschmid/mcp-cli
- Review MCP specification: https://modelcontextprotocol.io/docs
