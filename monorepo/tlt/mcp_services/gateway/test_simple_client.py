#!/usr/bin/env python3
"""Simple test using FastMCP client to test gateway"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastmcp import Client
    from fastmcp.transports.http import PythonHttpTransport
except ImportError:
    print("❌ Could not import FastMCP client. Testing with basic HTTP calls...")
    import httpx
    import json

async def test_with_basic_http():
    """Test using basic HTTP calls"""
    print("🧪 Testing Gateway with Basic HTTP")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        # Test simple GET to see what the endpoint expects
        try:
            response = await client.get("http://localhost:8003/mcp/")
            print(f"GET /mcp/ - Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            if response.text:
                print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"GET request failed: {e}")
        
        # Test with proper MCP initialization handshake
        try:
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await client.post(
                "http://localhost:8003/mcp/",
                json=init_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            print(f"\nMCP Initialize - Status: {response.status_code}")
            if response.status_code == 200:
                # Check for session in headers
                session_id = response.headers.get("x-mcp-session-id")
                print(f"Session ID: {session_id}")
                
                try:
                    result = response.json()
                    print(f"Initialize result: {json.dumps(result, indent=2)}")
                except:
                    print(f"Non-JSON response: {response.text}")
                
                # Now try to list tools
                tools_request = {
                    "jsonrpc": "2.0", 
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
                
                response = await client.post(
                    "http://localhost:8003/mcp/",
                    json=tools_request,
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json, text/event-stream"
                    }
                )
                print(f"\nTools List - Status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    if "result" in result and "tools" in result["result"]:
                        tools = result["result"]["tools"]
                        print(f"✅ Found {len(tools)} tools:")
                        for tool in tools[:3]:
                            print(f"  • {tool.get('name')}: {tool.get('description', 'No description')[:50]}...")
                    else:
                        print(f"Tools response: {json.dumps(result, indent=2)}")
                else:
                    print(f"Tools list failed: {response.text}")
            else:
                print(f"Initialize failed: {response.text}")
        except Exception as e:
            print(f"MCP request failed: {e}")

async def test_gateway_tools():
    """Test gateway tool calls after proper initialization"""
    print("\n🔧 Testing Gateway Tool Calls")
    print("=" * 40)
    
    async with httpx.AsyncClient() as client:
        # Initialize first
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
        
        init_response = await client.post(
            "http://localhost:8003/mcp/",
            json=init_request,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        )
        
        if init_response.status_code != 200:
            print(f"❌ Failed to initialize: {init_response.status_code}")
            return
        
        print("✅ Gateway initialized successfully")
        
        # Test gateway status (should work even with backend services down)
        status_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_gateway_status",
                "arguments": {}
            }
        }
        
        try:
            response = await client.post(
                "http://localhost:8003/mcp/",
                json=status_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            print(f"\nGateway Status - Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Gateway status call successful!")
                if "result" in result:
                    status = result["result"]
                    if isinstance(status, dict) and "gateway" in status:
                        print(f"   Gateway health: {status['gateway'].get('status', 'unknown')}")
                        print(f"   Backend services: {len(status.get('backend_services', {}))}")
            else:
                print(f"❌ Status call failed: {response.text}")
        except Exception as e:
            print(f"❌ Status call error: {e}")
        
        # Test a backend service call (should fail gracefully)
        events_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call", 
            "params": {
                "name": "list_all_events",
                "arguments": {"user_id": "test_user"}
            }
        }
        
        try:
            response = await client.post(
                "http://localhost:8003/mcp/",
                json=events_request,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream"
                }
            )
            print(f"\nList Events (Backend Down) - Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    if isinstance(result["result"], dict) and "error" in result["result"]:
                        print(f"✅ Graceful error handling: {result['result']['error']}")
                    else:
                        print(f"❓ Unexpected success: {result['result']}")
                elif "error" in result:
                    print(f"⚠️  MCP error: {result['error']}")
            else:
                print(f"❌ Events call failed: {response.text}")
        except Exception as e:
            print(f"❌ Events call error: {e}")

async def main():
    await test_with_basic_http()
    await test_gateway_tools()

if __name__ == "__main__":
    asyncio.run(main())