# MCP vs mcp-cli: Quick Reference Card

## One-Line Summary

**MCP** = The Protocol | **mcp-cli** = The Efficient Tool for AI Agents

---

## Core Differences

### MCP (Model Context Protocol)

```
What: Open standard for tool sharing
How: HTTP/Stdio endpoints serving tool schemas
When: Direct integrations, standardized interface
Token Cost: HIGH (load all tools upfront)
```

**Best Analogy:** A restaurant menu on a wall—everyone sees all dishes at once.

### mcp-cli

```
What: CLI tool for dynamic tool discovery
How: Queries specific tools on-demand
When: AI agents, token-efficient systems
Token Cost: LOW (load only what you use)
```

**Best Analogy:** A waiter who tells you about dishes as you ask.

---

## Feature Comparison Matrix

```
Feature                  | MCP    | mcp-cli
-------------------------|--------|----------
Tool Discovery          | Static | Dynamic
Context Load            | All    | On-Demand
Token Usage (60 tools)  | 47k    | 400
Setup Complexity        | Medium | Low
Server Required         | Yes    | No
AI Agent Ready          | Yes    | Yes (Better)
Scaling Limit           | Context| None
```

---

## Commands Comparison

### Listing Tools

**Traditional MCP:**
```bash
curl http://localhost:8000/mcp/tools/list
# Returns: All 60 tool schemas (47k tokens)
```

**mcp-cli:**
```bash
mcp-cli
# Returns: Just tool names (minimal tokens)
```

### Getting Tool Schema

**Traditional MCP:**
```bash
curl http://localhost:8000/mcp/tools/list | jq '.tools[5]'
# Already loaded (or fetch all again)
```

**mcp-cli:**
```bash
mcp-cli info github search_repositories
# Returns: Just this tool's schema (on-demand)
```

### Executing a Tool

**Traditional MCP:**
```bash
curl -X POST http://localhost:8000/mcp/tools/call \
  -d '{"name": "add_numbers", "arguments": {"a": 5, "b": 3}}'
```

**mcp-cli:**
```bash
mcp-cli call simple-calculator add_numbers '{"a": 5, "b": 3}'
```

---

## Architecture Comparison

### Traditional MCP Flow
```
1. Client connects
2. Server sends ALL tool schemas
3. Client loads into context
4. Client picks a tool
5. Client calls tool
```
**Problem:** Steps 1-3 consume massive tokens even if only 1 tool is used.

### mcp-cli Flow
```
1. Client asks: "What servers exist?"
2. Server responds: "These servers" (minimal)
3. Client asks: "What are params for tool X?"
4. Server responds: "Tool X schema" (on-demand)
5. Client calls tool
```
**Benefit:** Only load what you need.

---

## Decision Tree

```
Do you have a single MCP server?
├─ Yes + Direct HTTP needed? → Use Traditional MCP
└─ Yes + Want efficiency? → Use mcp-cli

Do you have 2+ MCP servers?
├─ Yes + Limited context window? → Use mcp-cli
└─ Yes + Unlimited resources? → Either works

Are you building for AI agents?
├─ Yes → Use mcp-cli (99% token savings)
└─ No → Use Traditional MCP

```

---

## Token Savings Example

**Scenario:** Building an AI agent with access to:
- GitHub MCP (20 tools)
- Filesystem MCP (15 tools)
- Email MCP (10 tools)
- Weather MCP (10 tools)
- Calendar MCP (5 tools)

**Total: 60 tools**

| Approach | Method | Tokens | Problem |
|----------|--------|--------|---------|
| Traditional MCP | Load all upfront | ~47,000 | 🔴 Context bloat |
| mcp-cli | List servers | ~100 | ✅ Minimal |
| mcp-cli | Inspect 1 tool | ~200 | ✅ On-demand |
| mcp-cli | Execute tool | ~300 | ✅ Complete |
| **Total (mcp-cli)** | All operations | ~600 | ✅ 99% savings |

---

## Implementation Complexity

### Traditional MCP

**Server side (Python FastAPI):**
```python
@app.post("/mcp/tools/list")
def list_tools():
    return {"tools": [schema for every tool]}

@app.post("/mcp/tools/call")
def call_tool(name, args):
    return TOOLS[name](**args)
```

**Complexity:** Medium (need to run server)

### mcp-cli

**Server side (Python stdio):**
```python
def main():
    while True:
        req = json.loads(input())
        if req["method"] == "tools/list":
            print(json.dumps(handle_list_tools()))
        elif req["method"] == "tools/call":
            print(json.dumps(handle_call_tool(req)))
```

**Client side:** Just use CLI
```bash
mcp-cli -c mcp_servers.json
```

**Complexity:** Low (mcp-cli handles everything)

---

## Hybrid Approach

**Best Practice:** Implement BOTH

```
1. Traditional MCP HTTP (app.py)
   ├─ For direct integrations
   ├─ For debugging
   └─ For non-AI-agent use cases

2. stdio-based MCP (mcp_server.py)
   ├─ For AI agent integration
   ├─ For token efficiency
   └─ For mcp-cli compatibility

Both share the same tool implementations (tools.py)
```

This is exactly what our example project does! ✅

---

## Practical Checklist

### Choose Traditional MCP if:
- [ ] Single MCP server
- [ ] Few tools (<10)
- [ ] Direct HTTP integration needed
- [ ] Not for AI agents
- [ ] Need full control over protocol

### Choose mcp-cli if:
- [ ] Multiple MCP servers
- [ ] Many tools (>10)
- [ ] Building for AI agents
- [ ] Token efficiency critical
- [ ] Want standardized solution

### Go Hybrid if:
- [ ] Supporting both use cases
- [ ] Want flexibility
- [ ] Building production system
- [ ] Need backward compatibility

---

## Common Misconceptions

| Misconception | Reality |
|---|---|
| "MCP and mcp-cli are competitors" | They're complementary—MCP is the protocol, mcp-cli is a tool that uses it |
| "mcp-cli requires less implementation" | Same tools, different interface |
| "Traditional MCP is outdated" | No, but mcp-cli is better for AI agents |
| "You must choose one" | Implement both for flexibility |
| "mcp-cli only works locally" | Works with both stdio and HTTP servers |

---

## Performance Metrics

### Startup Time
- **Traditional MCP:** ~200ms (start server) + ~100ms (load schemas) = ~300ms
- **mcp-cli:** ~50ms (process exists, pooled) + ~0ms (lazy load) = ~50ms
- **Winner:** mcp-cli ⚡

### Memory Usage
- **Traditional MCP:** All schemas in memory (~2-5MB for 60 tools)
- **mcp-cli:** Only current schemas (~50-100KB)
- **Winner:** mcp-cli 💾

### Token Efficiency
- **Traditional MCP:** 47,000 tokens for 60 tools
- **mcp-cli:** 400 tokens + on-demand queries
- **Winner:** mcp-cli 🚀 (99% reduction)

### Implementation Effort
- **Traditional MCP:** 2-3 hours (HTTP endpoints)
- **mcp-cli:** 1-2 hours (stdio handler) + CLI ready
- **Winner:** mcp-cli ⏱️

---

## Real-World Example: Our Calculator Project

```
Project: mcpPoc/

Implementation 1: Traditional MCP (app.py)
├─ HTTP endpoints at localhost:8000
├─ Full control
├─ Good for learning

Implementation 2: stdio MCP (mcp_server.py)
├─ Works with mcp-cli
├─ Token efficient
├─ Production ready

Both expose same tools (tools.py)
├─ add_numbers
├─ subtract_numbers
├─ divide_numbers
└─ get_current_time
```

**Result:** You can learn from both approaches, then choose which works best.

---

## The Future

```
2024: MCP Protocol Introduced
  ↓
2025: Static MCP Integration (token bloat)
  ↓
2026: mcp-cli (dynamic discovery) Becomes Standard ← You are here
  ↓
2027+: AI agents expect mcp-cli interface
        Dynamic discovery is default
        Token efficiency is baseline
```

---

## TL;DR

| Aspect | Answer |
|--------|--------|
| What's the difference? | MCP = protocol, mcp-cli = efficient tool |
| Token usage? | 47k vs 400 (99% savings with mcp-cli) |
| For AI agents? | mcp-cli (hands down) |
| For direct integration? | Traditional MCP works fine |
| Can I use both? | Yes! (Recommended) |
| Which is "better"? | Neither—different use cases |
| Future trend? | mcp-cli becoming standard |

---

## Resources

- [MCP Spec](https://modelcontextprotocol.io/)
- [mcp-cli GitHub](https://github.com/philschmid/mcp-cli)
- [Full Blog Post](./BLOG_MCP_vs_MCP_CLI.md)
- [Example Project](./README.md)

---

**Created:** February 2026  
**Example Project:** Simple Calculator MCP Server
