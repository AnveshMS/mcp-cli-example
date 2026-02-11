# MCP Server: Direct Call vs mcp-cli Comparison

## Executive Summary

The MCP server can be accessed in **two ways**:
1. **Via mcp-cli** (Recommended for AI agents) - Orchestration layer
2. **Direct stdio communication** (Manual protocol handling)

Both methods communicate with the same MCP server via stdio, but mcp-cli provides a convenience layer.

---

## Side-by-Side Comparison

### Method 1: Using mcp-cli ✅ Recommended

```bash
# Single command - mcp-cli handles everything
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}'
```

**What happens:**
```
AI Agent
   ↓
mcp-cli (reads mcp_servers.json)
   ↓ spawns process
   ↓ manages JSON-RPC protocol
   ↓ handles lifecycle
   ↓
MCP Server (mcp_server.py)
```

**Server Logs:**
```
2026-02-11 13:11:31 [MCP-SERVER] 🚀 MCP SERVER STARTED (stdio mode)
2026-02-11 13:11:31 [MCP-SERVER] 📥 Received request: method='initialize', id=0
2026-02-11 13:11:31 [MCP-SERVER] 🔧 INITIALIZE request received
2026-02-11 13:11:31 [MCP-SERVER] 📥 Received request: method='tools/call', id=1
2026-02-11 13:11:31 [MCP-SERVER] 🔨 CALL TOOL request received  
2026-02-11 13:11:31 [MCP-SERVER]    Tool: add_numbers
2026-02-11 13:11:31 [MCP-SERVER]    Arguments: {'a': 5, 'b': 3}
2026-02-11 13:11:31 [MCP-SERVER] ✓ Tool executed successfully: {'result': 8}
```

**Pros:**
- ✅ Simple one-line command
- ✅ Automatic server lifecycle management
- ✅ Protocol abstraction (don't need to know JSON-RPC details)
- ✅ Configuration-based (mcp_servers.json)
- ✅ Token-efficient for AI agents
- ✅ Error handling built-in

**Cons:**
- ⚠️ Requires mcp-cli installation
- ⚠️ Adds one more dependency

---

### Method 2: Direct stdio Communication ⚙️ Manual

```python
# Must manually handle JSON-RPC protocol
import subprocess
import json

process = subprocess.Popen(
    ["python", "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# 1. Initialize
request = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()
response = json.loads(process.stdout.readline())

# 2. Call tool
request = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "add_numbers",
        "arguments": {"a": 5, "b": 3}
    }
}
process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()
response = json.loads(process.stdout.readline())
result = json.loads(response['result']['content'][0]['text'])
print(result)  # {'result': 8}
```

**What happens:**
```
Your Code
   ↓ spawn subprocess
   ↓ write JSON-RPC to stdin
   ↓ read JSON-RPC from stdout
   ↓ parse responses
   ↓ handle errors manually
   ↓
MCP Server (mcp_server.py)
```

**Server Logs (Same as with mcp-cli):**
```
2026-02-11 13:14:54 [MCP-SERVER] 🚀 MCP SERVER STARTED (stdio mode)
2026-02-11 13:14:54 [MCP-SERVER] 📥 Received request: method='initialize', id=1
2026-02-11 13:14:54 [MCP-SERVER] 🔧 INITIALIZE request received
2026-02-11 13:14:54 [MCP-SERVER] 📥 Received request: method='tools/call', id=3
2026-02-11 13:14:54 [MCP-SERVER] 🔨 CALL TOOL request received  
2026-02-11 13:14:54 [MCP-SERVER]    Tool: add_numbers
2026-02-11 13:14:54 [MCP-SERVER]    Arguments: {'a': 10, 'b': 25}
2026-02-11 13:14:54 [MCP-SERVER] ✓ Tool executed successfully: {'result': 35}
```

**Pros:**
- ✅ No additional dependencies (just Python/subprocess)
- ✅ Full control over communication
- ✅ Can customize protocol handling

**Cons:**
- ❌ Must implement JSON-RPC protocol manually
- ❌ Must manage server process lifecycle
- ❌ Must handle errors manually
- ❌ More code to write and maintain
- ❌ Easy to make mistakes

---

## Key Observation: Server Logs Are THE SAME

**Important:** The MCP server (`mcp_server.py`) logs look identical whether called via:
- mcp-cli 
- Direct stdio communication

**Why?** Because both methods use the same stdio JSON-RPC protocol. The only difference is WHO is managing that protocol:
- **mcp-cli**: Handles it for you
- **Direct call**: You handle it yourself

---

## How to Detect Which Method is Being Used

You **cannot** detect from server logs alone whether mcp-cli or direct communication is being used, because both use the same protocol.

However, you can verify by:

### 1. Check the Calling Process

```python
# Add to mcp_server.py
import os
parent_pid = os.getppid()
parent_process = psutil.Process(parent_pid).name()
logger.info(f"Called by parent process: {parent_process}")
```

**Result:**
- With mcp-cli: `node.exe` or `mcp-cli.exe`
- Direct: `python.exe` or your custom script name

### 2. Check Environment Variables

mcp-cli might set specific environment variables:
```python
import os
if 'MCP_CLI_SESSION' in os.environ:
    logger.info("✅ Called via mcp-cli")
else:
    logger.info("⚙️  Called directly")
```

### 3. Count Tool List Requests

```python
# In mcp_server.py
if method == "tools/list":
    list_count += 1
    if list_count > 0:
        logger.info("📋 Dynamic discovery (mcp-cli style)")
```

**Heuristic:**
- mcp-cli often queries `tools/list` before calling specific tools
- Direct calls might skip `tools/list` if caller knows tool names

---

## Practical Recommendation

### For AI Agents: Use mcp-cli ✅

```json
// mcp_servers.json
{
  "mcpServers": {
    "simple-calculator": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "C:/Users/anbonagi/Downloads/mcpPoc"
    }
  }
}
```

```bash
# Agent calls mcp-cli, which manages everything
mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}'
```

**Benefits:**
- Token-efficient (lazy tool loading)
- Simple configuration
- Less code
- Better error handling

### For Custom Integrations: Direct Call ⚙️

Use direct stdio communication when:
- You need full control over the protocol
- You're building a custom MCP client
- You want to avoid mcp-cli dependency
- You're implementing custom caching/batching

---

## Complete Working Examples

### Example 1: With mcp-cli

See README.md Quick Start section:
```bash
.\node_modules\.bin\mcp-cli -c mcp_servers.json
```

### Example 2: Direct Call

Run the test script:
```bash
python test_direct_call.py
```

Both produce the same computational result, just different levels of abstraction!

---

## Summary Table

| Feature | mcp-cli | Direct stdio |
|---------|---------|--------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Simple | ⭐⭐ Complex |
| **Code Required** | 1 line | 20+ lines |
| **Dependencies** | Node.js + mcp-cli | None (Python only) |
| **Protocol Knowledge** | Not needed | Must know JSON-RPC |
| **Server Logs** | Same | Same |
| **Performance** | Fast | Fast (same) |
| **AI Agent Ready** | Yes ✅ | Requires wrapper |
| **Token Efficiency** | High ✅ | Depends on impl |
| **Error Handling** | Built-in | Manual |
| **Recommended For** | AI agents, quick dev | Custom clients |

---

## Bottom Line

> **Both methods talk to the same MCP server via stdio**
> 
> The difference is **who manages the JSON-RPC protocol**:
> - **mcp-cli** = Convenient orchestration layer (recommended)
> - **Direct call** = Manual protocol handling (advanced use case)
>
> **The server doesn't care which method you use!**
