#!/usr/bin/env python3
"""Test to see what headers and response the gateway provides"""

import asyncio
import httpx
import json

async def test_gateway_headers():
    """Test what the gateway returns on initialization"""
    print("🔍 Investigating Gateway Headers and Responses")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        print("🔄 Sending initialization request...")
        response = await client.post(
            "http://localhost:8003/mcp/",
            json=init_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers:")
        for name, value in response.headers.items():
            print(f"  {name}: {value}")
        
        print(f"\nResponse Content-Type: {response.headers.get('content-type')}")
        print(f"Response Length: {len(response.content)}")
        
        try:
            if response.content:
                json_response = response.json()
                print(f"\nJSON Response:")
                print(json.dumps(json_response, indent=2))
            else:
                print("\nNo response content")
        except Exception as e:
            print(f"\nNon-JSON response: {response.text}")
            print(f"Parse error: {e}")
        
        # Try a simple tool call without session to see what happens
        print("\n🔧 Testing tool call without session...")
        tool_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "get_gateway_status",
                "arguments": {}
            }
        }
        
        tool_response = await client.post(
            "http://localhost:8003/mcp/",
            json=tool_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        )
        
        print(f"Tool call status: {tool_response.status_code}")
        try:
            if tool_response.content:
                tool_json = tool_response.json()
                print(f"Tool response:")
                print(json.dumps(tool_json, indent=2))
        except:
            print(f"Tool response text: {tool_response.text}")

if __name__ == "__main__":
    asyncio.run(test_gateway_headers())