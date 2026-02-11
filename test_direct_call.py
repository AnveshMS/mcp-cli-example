#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to call MCP server directly (without mcp-cli)
This demonstrates the difference between using mcp-cli vs direct server communication
"""

import subprocess
import json
import sys
import io

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def send_request(process, method, params=None, request_id=1):
    """Send a JSON-RPC request to the MCP server"""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method
    }
    if params:
        request["params"] = params
    
    # Send request
    request_json = json.dumps(request) + "\n"
    print(f"\n📤 SENDING: {request_json.strip()}")
    process.stdin.write(request_json)
    process.stdin.flush()
    
    # Read response
    response_line = process.stdout.readline()
    print(f"📥 RECEIVED: {response_line.strip()}")
    
    try:
        return json.loads(response_line)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        return None


def main():
    print("=" * 70)
    print("🔴 DIRECT MCP SERVER CALL (Without mcp-cli)")
    print("=" * 70)
    print("\nThis demonstrates calling the MCP server directly via stdio")
    print("Notice: NO mcp-cli orchestration layer!")
    print("=" * 70)
    
    # Start the MCP server process
    process = subprocess.Popen(
        ["python", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        print("\n🔹 Step 1: Initialize the server")
        response = send_request(process, "initialize", request_id=1)
        if response and "result" in response:
            print(f"✅ Server initialized: {response['result']['serverInfo']['name']}")
        
        print("\n🔹 Step 2: List available tools")
        response = send_request(process, "tools/list", request_id=2)
        if response and "result" in response:
            tools = response['result']['tools']
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        
        print("\n🔹 Step 3: Call add_numbers tool")
        response = send_request(
            process, 
            "tools/call", 
            params={
                "name": "add_numbers",
                "arguments": {"a": 10, "b": 25}
            },
            request_id=3
        )
        if response and "result" in response:
            result_text = response['result']['content'][0]['text']
            result = json.loads(result_text)
            print(f"✅ Calculation result: {result}")
        
        print("\n🔹 Step 4: Call multiply_numbers tool")
        response = send_request(
            process, 
            "tools/call", 
            params={
                "name": "multiply_numbers",
                "arguments": {"a": 7, "b": 6}
            },
            request_id=4
        )
        if response and "result" in response:
            result_text = response['result']['content'][0]['text']
            result = json.loads(result_text)
            print(f"✅ Calculation result: {result}")
        
    finally:
        # Close the process
        process.stdin.close()
        process.wait(timeout=2)
        
        # Print server stderr (where our logs go)
        stderr_output = process.stderr.read()
        if stderr_output:
            print("\n" + "=" * 70)
            print("📋 SERVER LOGS (from stderr):")
            print("=" * 70)
            print(stderr_output)
    
    print("\n" + "=" * 70)
    print("🎯 KEY DIFFERENCE:")
    print("=" * 70)
    print("✅ WITH mcp-cli:")
    print("   - mcp-cli handles JSON-RPC protocol")
    print("   - mcp-cli manages server lifecycle")
    print("   - Token-efficient dynamic discovery")
    print("   - Easier for AI agents to use")
    print()
    print("⚠️  WITHOUT mcp-cli (direct call - what we just did):")
    print("   - Manual JSON-RPC protocol handling")
    print("   - Manual server process management")
    print("   - Must know all protocol details")
    print("   - More complex for agents")
    print("=" * 70)


if __name__ == "__main__":
    main()
