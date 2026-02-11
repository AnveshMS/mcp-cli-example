# MCP-CLI vs Direct Server Call - Demonstration

This script demonstrates the difference between:
1. **Agent → mcp-cli → MCP Server** (Token-efficient, dynamic discovery)
2. **Agent → MCP Server directly** (Would load all tools upfront)

## How to Verify Which Method is Being Used

### Test 1: Call via mcp-cli (Recommended)

```bash
# This is what an AI agent should use
.\node_modules\.bin\mcp-cli -c mcp_servers.json call simple-calculator add_numbers '{"a": 5, "b": 3}'
```

**What you'll see in the logs:**
```
2026-02-11 10:30:00 [MCP-SERVER] ============================================================
2026-02-11 10:30:00 [MCP-SERVER] 🚀 MCP SERVER STARTED (stdio mode)
2026-02-11 10:30:00 [MCP-SERVER]    Waiting for JSON-RPC requests from mcp-cli...
2026-02-11 10:30:00 [MCP-SERVER] ============================================================

2026-02-11 10:30:00 [MCP-SERVER] 📥 Received request: method='initialize', id=1
2026-02-11 10:30:00 [MCP-SERVER] 🔧 INITIALIZE request received (called by mcp-cli)
2026-02-11 10:30:00 [MCP-SERVER] ✓ Initialized: Simple Calculator MCP Server

2026-02-11 10:30:00 [MCP-SERVER] 📥 Received request: method='tools/call', id=2
2026-02-11 10:30:00 [MCP-SERVER] 🔨 CALL TOOL request received (called by mcp-cli)
2026-02-11 10:30:00 [MCP-SERVER]    Tool: add_numbers
2026-02-11 10:30:00 [MCP-SERVER]    Arguments: {'a': 5, 'b': 3}
2026-02-11 10:30:00 [MCP-SERVER] ✓ Tool executed successfully: {'result': 8}
```

**Key Indicators:**
- ✅ Server logs show it's receiving requests from mcp-cli
- ✅ Only ONE tool is called (add_numbers) - not all tools loaded
- ✅ Token-efficient: Agent doesn't see all tool schemas upfront

---

### Test 2: List all tools via mcp-cli

```bash
# This shows mcp-cli querying available tools
.\node_modules\.bin\mcp-cli -c mcp_servers.json
```

**What you'll see:**
```
2026-02-11 10:31:00 [MCP-SERVER] 📥 Received request: method='initialize', id=1
2026-02-11 10:31:00 [MCP-SERVER] 🔧 INITIALIZE request received (called by mcp-cli)

2026-02-11 10:31:00 [MCP-SERVER] 📥 Received request: method='tools/list', id=2
2026-02-11 10:31:00 [MCP-SERVER] 📋 LIST TOOLS request received (called by mcp-cli)
2026-02-11 10:31:00 [MCP-SERVER] ✓ Returning 4 tools: ['add_numbers', 'subtract_numbers', 'multiply_numbers', 'divide_numbers']
```

**Key Indicators:**
- ✅ mcp-cli queries for tool list
- ✅ Agent can then choose which tool to call
- ✅ Dynamic discovery pattern

---

### Test 3: Direct Server Call (NOT via mcp-cli)

If you were to call the server directly (bypassing mcp-cli):

```bash
# Direct stdio communication (what mcp-cli does internally)
echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | python mcp_server.py
```

**What you'll see:**
```
2026-02-11 10:32:00 [MCP-SERVER] 🚀 MCP SERVER STARTED (stdio mode)
2026-02-11 10:32:00 [MCP-SERVER] 📥 Received request: method='initialize', id=1
2026-02-11 10:32:00 [MCP-SERVER] 🔧 INITIALIZE request received (called by mcp-cli)
```

**Key Difference:**
- ⚠️ This is raw JSON-RPC communication
- ⚠️ No mcp-cli orchestration layer
- ⚠️ Agent would need to handle protocol manually

---

## Visual Comparison

### ✅ With mcp-cli (What AI Agents Should Use)

```
┌─────────────┐
│  AI Agent   │
│             │
│ "Add 5+3"   │
└──────┬──────┘
       │
       │ Uses mcp-cli
       ▼
┌─────────────────────────────────────┐
│  mcp-cli (Token-Efficient Layer)    │
│                                     │
│  1. Query: What tools exist?        │
│  2. Parse: "add_numbers" needed     │
│  3. Call: Only that specific tool   │
└────────┬────────────────────────────┘
         │
         │ JSON-RPC via stdio
         ▼
┌─────────────────────────┐
│   MCP Server            │
│   (mcp_server.py)       │
│                         │
│   Logs show:            │
│   📥 tools/call         │
│   🔨 add_numbers called │
│   ✓ Result: 8           │
└─────────────────────────┘
```

### ❌ Without mcp-cli (Traditional MCP - Less Efficient)

```
┌─────────────┐
│  AI Agent   │
│             │
│ "Add 5+3"   │
└──────┬──────┘
       │
       │ Loads ALL tool schemas upfront
       ▼
┌──────────────────────────────────┐
│   MCP Server                     │
│                                  │
│   Agent receives:                │
│   • add_numbers schema           │
│   • subtract_numbers schema      │
│   • multiply_numbers schema      │
│   • divide_numbers schema        │
│                                  │
│   ⚠️ Higher token cost!          │
└──────────────────────────────────┘
```

---

## Verification Checklist

When an AI agent calls your calculator, verify it's using mcp-cli by checking:

| Indicator | mcp-cli ✅ | Direct Call ❌ |
|-----------|-----------|----------------|
| Server logs show "called by mcp-cli" | Yes | No |
| Only requested tool is invoked | Yes | No |
| Dynamic tool discovery (tools/list) | Yes | Maybe |
| Token-efficient (lazy loading) | Yes | No |
| mcp-cli command in config | Yes | No |

---

## How mcp-cli Configuration Proves It's Being Used

Check `mcp_servers.json`:

```json
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

When an agent uses this configuration with mcp-cli:
1. ✅ mcp-cli reads this config
2. ✅ mcp-cli spawns `python mcp_server.py`
3. ✅ mcp-cli manages stdio communication
4. ✅ Server logs show the requests

**Bottom Line:** If your server logs show the emoji indicators and structured logs, your MCP server is being invoked correctly by mcp-cli!
