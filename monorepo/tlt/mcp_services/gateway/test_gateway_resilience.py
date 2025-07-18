#!/usr/bin/env python3
"""Test script to verify gateway resilience when backend services are unavailable"""

import asyncio
import httpx
import json

async def test_gateway_with_missing_services():
    """Test gateway behavior when backend services are down"""
    print("🧪 Testing Gateway Resilience")
    print("=" * 40)
    
    gateway_url = "http://localhost:8003/mcp/"
    
    # Test cases: tool calls that should fail gracefully
    test_cases = [
        {
            "name": "list_all_events",
            "description": "List events (Event Manager service down)",
            "request": {
                "jsonrpc": "2.0",
                "id": "test_1",
                "method": "tools/call",
                "params": {
                    "name": "list_all_events",
                    "arguments": {"user_id": "test_user"}
                }
            }
        },
        {
            "name": "create_rsvp", 
            "description": "Create RSVP (RSVP service down)",
            "request": {
                "jsonrpc": "2.0",
                "id": "test_2", 
                "method": "tools/call",
                "params": {
                    "name": "create_rsvp",
                    "arguments": {
                        "event_id": "event_123",
                        "user_id": "user_456", 
                        "emoji": "👍"
                    }
                }
            }
        },
        {
            "name": "get_gateway_status",
            "description": "Get gateway status (should work)",
            "request": {
                "jsonrpc": "2.0",
                "id": "test_3",
                "method": "tools/call", 
                "params": {
                    "name": "get_gateway_status",
                    "arguments": {}
                }
            }
        }
    ]
    
    async with httpx.AsyncClient() as client:
        print("📡 Testing tool calls with backend services down...\n")
        
        for test_case in test_cases:
            print(f"🔍 Testing: {test_case['description']}")
            print(f"   Tool: {test_case['name']}")
            
            try:
                response = await client.post(
                    gateway_url,
                    json=test_case['request'],
                    headers={"Content-Type": "application/json"},
                    timeout=10.0
                )
                
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if "error" in result:
                        print(f"   ❌ MCP Error: {result['error']}")
                    elif "result" in result:
                        if isinstance(result['result'], dict) and "error" in result['result']:
                            print(f"   ⚠️  Service Error: {result['result']['error']}")
                            print(f"   ✅ Graceful handling: Service unavailable detected")
                        else:
                            print(f"   ✅ Success: Tool executed successfully")
                            if test_case['name'] == 'get_gateway_status':
                                print(f"   📊 Gateway Status: {result['result'].get('gateway', {}).get('status', 'unknown')}")
                    else:
                        print(f"   ❓ Unexpected response format")
                        
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except httpx.RequestError as e:
                print(f"   ❌ Connection Error: {e}")
            except Exception as e:
                print(f"   ❌ Unexpected Error: {e}")
            
            print()
        
        # Test tools list
        print("📋 Testing tools discovery...")
        try:
            tools_request = {
                "jsonrpc": "2.0",
                "id": "tools_list",
                "method": "tools/list",
                "params": {}
            }
            
            response = await client.post(
                gateway_url,
                json=tools_request,
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "tools" in result["result"]:
                    tools = result["result"]["tools"]
                    print(f"   ✅ Found {len(tools)} available tools")
                    
                    # Show some example tools
                    for tool in tools[:5]:
                        print(f"      • {tool.get('name', 'unknown')}: {tool.get('description', 'No description')}")
                    
                    if len(tools) > 5:
                        print(f"      ... and {len(tools) - 5} more tools")
                else:
                    print(f"   ❓ Unexpected tools response format")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error listing tools: {e}")
    
    print("\n🎯 Test Summary:")
    print("- Gateway should handle missing backend services gracefully")
    print("- Tools should return service unavailable errors instead of crashing")
    print("- Gateway-local tools (like get_gateway_status) should still work")
    print("- Tools discovery should work regardless of backend service status")

if __name__ == "__main__":
    asyncio.run(test_gateway_with_missing_services())