# MCP vs mcp-cli: Understanding the Protocol and the Tool

**Published:** February 2026  
**Author:** Technical Documentation  
**Reading Time:** 12 minutes  

---

## Introduction

The AI agent ecosystem is evolving rapidly, and with it comes a scaling challenge that many developers are hitting: **context window bloat**. When building systems that integrate with multiple MCP (Model Context Protocol) servers, you're forced to load all tool definitions upfront—consuming thousands of tokens just to describe what tools *could* be available.

Enter **mcp-cli**: a lightweight tool that changes how we interact with MCP servers. But before diving into mcp-cli, it's essential to understand the foundational protocol itself, the design trade-offs between static and dynamic approaches, and how they differ fundamentally.

This blog explores these differences and uses a real hands-on project—a simple calculator MCP server—to demonstrate both approaches in action.

---

## Part 1: Understanding MCP (Model Context Protocol)

### What is MCP?

The **Model Context Protocol (MCP)** is an open standard for connecting AI agents and applications to external tools, APIs, and data sources. Think of it as a universal interface that allows:

- **AI Agents** (Claude, Gemini, etc.) to discover and call tools
- **Tool Providers** to expose capabilities in a standardized way
- **Seamless Integration** between diverse systems without custom adapters

### How MCP Works

MCP operates on a simple premise: define tools with clear schemas, and let clients discover and invoke them.

**Basic MCP Flow:**
```
Tool Provider (MCP Server)
  ↓
[Tool Definitions + Schemas]
  ↓
AI Agent / Client
  ↓
[Discover Tools] → [Invoke Tools] → [Get Results]
```

**Example:** A GitHub MCP server exposes tools like:
- `search_repositories` - Search GitHub repos
- `create_issue` - Create a GitHub issue
- `list_pull_requests` - List open PRs

Each tool comes with a JSON schema describing its parameters, types, and requirements.

### The Static Integration Problem

Traditionally, MCP integration works like this:

1. **Startup:** Load ALL tool definitions from all servers
2. **Context Window:** Send every tool schema to the AI model
3. **Invocation:** Model chooses which tool to call
4. **Execution:** Tool is invoked and result returned

**The Problem:**

When you have multiple MCP servers, the token cost becomes substantial:

| Scenario | Token Count |
|----------|-------------|
| 6 MCP Servers, 60 tools (static loading) | ~47,000 tokens |
| After dynamic discovery | ~400 tokens |
| **Token Reduction** | **99% 🚀** |

For a production system with 10+ servers exposing 100+ tools, you're burning through thousands of tokens just describing capabilities, leaving less context for actual reasoning and problem-solving.

**Key Issues:**
- ❌ Reduced effective context length for actual work
- ❌ More frequent context compactions
- ❌ Hard limits on simultaneous MCP servers
- ❌ Higher API costs

---

## Part 2: Enter mcp-cli – Dynamic Context Discovery

### What is mcp-cli?

**mcp-cli** is a lightweight CLI tool (written in Bun, compiled to a single binary) that implements **dynamic context discovery** for MCP servers. Instead of loading everything upfront, it pulls in information only when needed.

### Static vs. Dynamic: The Paradigm Shift

**Traditional MCP (Static Context):**
```
AI Agent Says: "Load all tool definitions from all servers"
↓
Context Window Bloat ❌
↓
Limited space for reasoning
```

**mcp-cli (Dynamic Discovery):**
```
AI Agent Says: "What servers exist?"
↓ mcp-cli responds
AI Agent Says: "What are the params for tool X?"
↓ mcp-cli responds
AI Agent Says: "Execute tool X"
↓ mcp-cli executes and responds
```

**Result:** You only pay for information you actually use. ✅

### Core Capabilities

mcp-cli provides three primary commands:

#### 1. **Discover** - What servers and tools exist?
```bash
mcp-cli
```
Lists all configured MCP servers and their tools.

#### 2. **Inspect** - What does a specific tool do?
```bash
mcp-cli info <server> <tool>
```
Returns the full JSON schema for a tool (parameters, descriptions, types).

#### 3. **Execute** - Run a tool
```bash
mcp-cli call <server> <tool> '{"arg": "value"}'
```
Executes the tool and returns results.

### Key Features of mcp-cli

| Feature | Benefit |
|---------|---------|
| **Stdio & HTTP Support** | Works with both local and remote MCP servers |
| **Connection Pooling** | Lazy-spawn daemon avoids repeated startup overhead |
| **Tool Filtering** | Control which tools are available via `allowedTools`/`disabledTools` |
| **Glob Searching** | Find tools matching patterns: `mcp-cli grep "*mail*"` |
| **AI Agent Ready** | Designed for use in system instructions and agent skills |
| **Lightweight** | Single binary, minimal dependencies |

---

## Part 3: Hands-On Comparison with Our Calculator Project

Let me demonstrate both approaches using a real project: a **Simple Calculator MCP Server**.

### The Project Structure

```
mcpPoc/
├── tools.py              # Tool implementations (shared)
├── app.py               # FastAPI server (HTTP endpoints)
├── mcp_server.py        # Stdio-based MCP server
├── mcp_servers.json     # mcp-cli configuration
└── README.md
```

### Approach 1: Traditional HTTP MCP Integration

Our **app.py** implements the HTTP-based MCP protocol with endpoints:

```python
# app.py - Traditional MCP HTTP Endpoints
@app.post("/mcp/tools/list")
def mcp_list_tools(request: MCPRequest) -> MCPResponse:
    """Lists all tools - sent upfront to client"""
    tools = []
    for name, tool_info in TOOLS.items():
        tools.append(build_tool_schema(name, tool_info))
    return MCPResponse(
        jsonrpc="2.0",
        id=request.id,
        result={"tools": tools}  # ALL tools loaded at once
    )

@app.post("/mcp/tools/call")
def mcp_call_tool(request: MCPRequest) -> MCPResponse:
    """Execute a specific tool"""
    # ... implementation
```

**How it's used:**
1. Client makes request to `/mcp/tools/list`
2. Server responds with **all** 4 tools at once:
   - add_numbers
   - subtract_numbers
   - divide_numbers
   - get_current_time
3. Client loads all schemas into context
4. Client decides which to call

**Token Cost:** All 4 tools' schemas loaded (even if only 1 is needed)

### Approach 2: mcp-cli with Stdio Protocol

Our **mcp_server.py** implements the stdio-based MCP server:

```python
# mcp_server.py - Stdio-based MCP Server
def main():
    """Main loop - read from stdin, process, write to stdout"""
    while True:
        line = sys.stdin.readline()
        request = json.loads(line.strip())
        method = request.get("method")
        
        # Route to appropriate handler
        if method == "initialize":
            response = handle_initialize(request_id)
        elif method == "tools/list":
            response = handle_list_tools(request_id)
        elif method == "tools/call":
            response = handle_call_tool(request_id, params)
        
        print(json.dumps(response))
        sys.stdout.flush()
```

**How it's used with mcp-cli:**

```json
// mcp_servers.json
{
  "mcpServers": {
    "simple-calculator": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

Now mcp-cli communicates via stdio:
```bash
# Step 1: Discover (lazy - just lists names)
.\node_modules\.bin\mcp-cli -c mcp_servers.json
# Output: simple-calculator → add_numbers, subtract_numbers, ...

# Step 2: Inspect (only fetch what you need)
.\node_modules\.bin\mcp-cli -c mcp_servers.json info simple-calculator add_numbers
# Output: Just the schema for add_numbers

# Step 3: Execute
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}'
# Output: {"result": 8}
```

---

## Part 4: Detailed Comparison Table

| Aspect | **Traditional MCP** | **mcp-cli** |
|--------|-------------------|-----------|
| **Protocol** | HTTP/REST or Stdio | Stdio/HTTP (via CLI) |
| **Context Loading** | Static (upfront) | Dynamic (on-demand) |
| **Tool Discovery** | All at once | Lazy enumeration |
| **Schema Inspection** | Pre-loaded | On-request |
| **Token Usage** | High (~47k for 60 tools) | Low (~400 for 60 tools) |
| **Best For** | Direct server integration | AI agent tool use |
| **Implementation** | Server-side focus | CLI-side focus |
| **Complexity** | Medium | Low (CLI handles it) |
| **Startup Time** | One call | Multiple calls (optimized) |
| **Scaling** | Limited by context | Unlimited (pay per use) |
| **Integration** | Custom implementation | Pre-built mcp-cli |

---

## Part 5: Practical Hands-On Examples

### Example 1: Basic Tool Discovery

**Traditional Approach:**
```bash
# Must start FastAPI server first
uvicorn app:app

# Then in another terminal, get all tools
curl http://localhost:8000/mcp/tools/list
# Returns: 4 tools with all schemas (large response)
```

**mcp-cli Approach:**
```bash
# No server startup needed
.\node_modules\.bin\mcp-cli -c mcp_servers.json
# Returns: Just tool names (minimal)
```

### Example 2: Get Detailed Schema

**Traditional Approach:**
```bash
# All schemas already loaded (or need separate call per tool)
curl http://localhost:8000/mcp/tools/list | jq '.result.tools[0]'
```

**mcp-cli Approach:**
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json info simple-calculator add_numbers
# Returns: Full schema for just this tool
```

### Example 3: Execute a Tool

**Traditional Approach:**
```bash
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "add_numbers", "arguments": {"a": 5, "b": 3}}'
```

**mcp-cli Approach:**
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}'
```

### Example 4: Integration with AI Agents

**System Instruction for AI Agent using mcp-cli:**

```
## Available Tools via MCP

You have access to calculator tools through mcp-cli:

Commands:
- mcp-cli                           # List servers and tools
- mcp-cli info simple-calculator    # Show all tools
- mcp-cli info simple-calculator <tool>  # Get tool schema
- mcp-cli call simple-calculator <tool> '<json>'  # Execute tool

Workflow:
1. Use "mcp-cli" to discover available tools
2. Use "mcp-cli info simple-calculator add_numbers" to get schema if needed
3. Use "mcp-cli call simple-calculator add_numbers '{"a": 5, "b": 3}'" to execute

This approach keeps your context window clean by only loading tool info when needed.
```

---

## Part 6: When to Use Each Approach

### Use **Traditional MCP (HTTP Endpoints)** when:
- ✅ Building a direct server integration
- ✅ You have few tools (< 10) and don't care about context waste
- ✅ You need full control over HTTP requests/responses
- ✅ You're building a specialized integration (not AI agents)
- ✅ Real-time synchronous calls are required

### Use **mcp-cli** when:
- ✅ Integrating with AI agents (Claude, Gemini, etc.)
- ✅ You have multiple MCP servers (> 2-3)
- ✅ Token efficiency is critical
- ✅ You want a standardized, battle-tested tool
- ✅ You prefer CLI-based automation
- ✅ Connection pooling and lazy loading are beneficial
- ✅ You're building agent skills or system instructions

---

## Part 7: Advanced Features of mcp-cli

### 1. Tool Filtering

Control which tools are exposed:

```json
{
  "mcpServers": {
    "simple-calculator": {
      "command": "python",
      "args": ["mcp_server.py"],
      "allowedTools": ["add_numbers", "subtract_numbers"],
      "disabledTools": ["divide_numbers"]
    }
  }
}
```

Now only add_numbers and subtract_numbers are available.

### 2. Glob-based Search

```bash
.\node_modules\.bin\mcp-cli grep "*numbers*"
# Returns all tools with "numbers" in the name
```

### 3. Connection Pooling

mcp-cli uses lazy-spawn daemon to avoid repeated server startup:

```bash
# Force fresh connection (no pooling)
$env:MCP_NO_DAEMON="1"; mcp-cli

# Change idle timeout (default 60s)
$env:MCP_DAEMON_TIMEOUT="120"; mcp-cli
```

### 4. Complex JSON Piping

```bash
# Use heredoc for complex JSON
.\node_modules\.bin\mcp-cli call server tool <<EOF
{
  "nested": {
    "field": "value with 'quotes'"
  }
}
EOF
```

---

## Part 8: Implementation Comparison

### HTTP MCP Server Implementation (app.py)

```python
@app.post("/mcp/tools/list")
def mcp_list_tools(request: MCPRequest):
    # Build and return all schemas
    tools = [build_tool_schema(name, tool) for name, tool in TOOLS.items()]
    return {"tools": tools}

@app.post("/mcp/tools/call")
def mcp_call_tool(request: MCPRequest):
    # Execute single tool
    result = TOOLS[name]["function"](**arguments)
    return {"result": result}
```

**Pros:**
- ✅ Full control
- ✅ Standard HTTP
- ✅ Easy to debug (curl)

**Cons:**
- ❌ All tools loaded upfront
- ❌ Token inefficient
- ❌ Requires running server

### Stdio MCP Server Implementation (mcp_server.py)

```python
def main():
    while True:
        request = json.loads(sys.stdin.readline())
        if request["method"] == "tools/list":
            response = handle_list_tools(request["id"])
        elif request["method"] == "tools/call":
            response = handle_call_tool(request["id"], request["params"])
        print(json.dumps(response))
        sys.stdout.flush()
```

**Pros:**
- ✅ Dynamic discovery
- ✅ Token efficient (99% reduction)
- ✅ mcp-cli ready
- ✅ No server to run

**Cons:**
- ❌ Stdin/stdout protocol
- ❌ Slightly harder to debug manually

---

## Part 9: The Future: AI Agents and mcp-cli

The evolution is clear:

```
Phase 1: Direct API Integration
├─ Tools hardcoded
├─ No discovery
└─ Limited scalability

Phase 2: MCP Protocol (Static)
├─ Standardized schemas
├─ Tool discovery
├─ Context bloat ❌

Phase 3: MCP + mcp-cli (Dynamic)
├─ Standardized schemas
├─ Dynamic discovery ✅
├─ Token efficient ✅
├─ AI agent ready ✅
└─ Unlimited scalability ✅
```

**Key Insight:** As AI agents become more capable and integrate with more tools, dynamic discovery becomes essential. mcp-cli is the standardized solution.

---

## Part 10: Getting Started with Both

### Quick Setup: Our Calculator Project

**Option 1: Try Traditional MCP (HTTP)**
```bash
# Start server
uvicorn app:app --reload

# Test in another terminal
curl http://localhost:8000/mcp/tools/list
```

**Option 2: Try mcp-cli**
```bash
# No server startup
bun install mcp-cli@github:philschmid/mcp-cli

# Discover tools
.\node_modules\.bin\mcp-cli -c mcp_servers.json

# Call a tool
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 10, "b": 20}'
```

---

## Conclusion

**MCP (Model Context Protocol)** defines the standard for tool sharing and discovery. **mcp-cli** is the practical tool that makes MCP efficient for AI agents by implementing dynamic context discovery.

The fundamental difference:

| | MCP | mcp-cli |
|---|-----|---------|
| **What** | The protocol standard | The CLI tool |
| **Where** | Both server and client | Client-side CLI |
| **Problem Solved** | Tool standardization | Context bloat |
| **Architecture** | Protocol | Implementation |

Think of it this way: **MCP is the language, mcp-cli is the interpreter that speaks fluently.**

For AI agent systems, dynamic discovery via mcp-cli is becoming the standard. For direct integrations, traditional MCP HTTP endpoints work fine. The choice depends on your use case, but increasingly, the industry is trending toward mcp-cli for its efficiency and scalability.

---

## Resources

- [MCP Specification](https://modelcontextprotocol.io/)
- [mcp-cli GitHub](https://github.com/philschmid/mcp-cli)
- [Our Example Project](https://github.com/your-repo/mcpPoc)
- [Philipp Schmid's Blog](https://www.philschmid.de/mcp-cli)

---

## About This Article

This blog post demonstrates the differences between MCP and mcp-cli using a real, working calculator project that implements both approaches. The project includes:

- ✅ HTTP-based MCP server (app.py)
- ✅ Stdio-based MCP server for mcp-cli (mcp_server.py)
- ✅ Shared tool implementations (tools.py)
- ✅ mcp-cli configuration (mcp_servers.json)
- ✅ Full documentation and examples

All code is production-ready and demonstrates best practices for both approaches.

---

**Questions? Feedback?** Feel free to reach out or open issues on the project repository.

