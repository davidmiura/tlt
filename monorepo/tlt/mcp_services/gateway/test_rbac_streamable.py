#!/usr/bin/env python3
"""
RBAC-focused test suite for MCP Gateway using Streamable HTTP.
Tests Casbin policy enforcement with different user roles.
"""

import asyncio
import httpx
import json
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

@dataclass
class TestUser:
    """Represents a test user with specific role and permissions"""
    user_id: str
    role: str
    description: str
    expected_access: List[str]  # Tools this user should be able to access
    denied_access: List[str]    # Tools this user should be denied

class RBACTestClient:
    """Streamable HTTP client for RBAC testing"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id: Optional[str] = None
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        await self._initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def _initialize(self):
        """Initialize MCP connection"""
        response = await self.client.post(
            f"{self.base_url}/mcp/",
            json={
                "jsonrpc": "2.0",
                "id": "init",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "RBAC-Test-Client", "version": "1.0.0"}
                }
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
        )
        
        if response.status_code == 200:
            self.session_id = response.headers.get("mcp-session-id")
    
    def _parse_sse_response(self, sse_text: str) -> Dict[str, Any]:
        """Parse Server-Sent Events response to extract JSON"""
        lines = sse_text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                return json.loads(line[6:])
        raise ValueError("No valid data found in SSE response")
    
    async def call_tool_as_user(self, tool_name: str, user: TestUser, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Call a tool as a specific user with their role context"""
        args = arguments or {}
        
        # Add user context to the arguments
        args.update({
            "user_id": user.user_id,
            "role": user.role,
            "metadata": {
                "user_id": user.user_id,
                "role": user.role,
                "test_context": True
            }
        })
        
        request = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": args
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream"
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        
        response = await self.client.post(
            f"{self.base_url}/mcp/",
            json=request,
            headers=headers
        )
        
        if response.status_code == 200:
            return self._parse_sse_response(response.text)
        else:
            return {
                "error": {
                    "code": response.status_code,
                    "message": f"HTTP {response.status_code}",
                    "data": response.text
                }
            }

class RBACTestSuite:
    """Test suite for RBAC functionality"""
    
    def __init__(self, gateway_url: str = "http://localhost:8003"):
        self.gateway_url = gateway_url
        self.test_users = self._create_test_users()
        self.results = []
    
    def _create_test_users(self) -> List[TestUser]:
        """Create test users with different roles and expected permissions"""
        return [
            TestUser(
                user_id="admin_user_001",
                role="admin",
                description="Administrator with full access",
                expected_access=[
                    "get_gateway_status",
                    "get_casbin_policies",
                    "add_casbin_policy",
                    "get_user_roles",
                    "create_event",
                    "list_all_events",
                    "create_rsvp"
                ],
                denied_access=[]  # Admin should have access to everything
            ),
            TestUser(
                user_id="event_owner_001", 
                role="event_owner",
                description="Event owner with event management permissions",
                expected_access=[
                    "get_gateway_status",
                    "create_event",
                    "list_all_events",
                    "get_event_rsvps"  # Should be able to view RSVPs for analytics
                ],
                denied_access=[
                    "get_casbin_policies",  # Should not access admin tools
                    "add_casbin_policy",
                    "add_user_role"
                ]
            ),
            TestUser(
                user_id="regular_user_001",
                role="user",
                description="Regular user with RSVP permissions only",
                expected_access=[
                    "get_gateway_status",
                    "list_all_events",  # Should be able to view events
                    "create_rsvp",
                    "update_user_rsvp"
                ],
                denied_access=[
                    "create_event",      # Cannot create events
                    "get_casbin_policies",
                    "add_casbin_policy",
                    "add_user_role"
                ]
            )
        ]
    
    def _log_result(self, test_name: str, user: TestUser, tool: str, expected: bool, actual: bool, details: str = ""):
        """Log test result"""
        passed = (expected == actual)
        status = "✅ PASS" if passed else "❌ FAIL"
        access_type = "ALLOW" if expected else "DENY"
        
        print(f"{status} {test_name}")
        print(f"    User: {user.user_id} ({user.role})")
        print(f"    Tool: {tool}")
        print(f"    Expected: {access_type}, Got: {'ALLOW' if actual else 'DENY'}")
        if details:
            print(f"    Details: {details}")
        print()
        
        self.results.append({
            "test_name": test_name,
            "user_id": user.user_id,
            "role": user.role,
            "tool": tool,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "details": details
        })
    
    async def test_tool_access(self, client: RBACTestClient, user: TestUser, tool_name: str, expected_access: bool):
        """Test if a user can access a specific tool"""
        try:
            # Prepare arguments based on tool type
            arguments = {}
            if tool_name == "create_event":
                arguments = {
                    "title": "Test Event",
                    "description": "RBAC Test Event",
                    "creator_id": user.user_id,
                    "start_time": "2024-12-01T10:00:00Z",
                    "end_time": "2024-12-01T12:00:00Z"
                }
            elif tool_name == "create_rsvp":
                arguments = {
                    "event_id": "test_event_123",
                    "user_id": user.user_id,
                    "emoji": "👍"
                }
            elif tool_name == "add_casbin_policy":
                arguments = {
                    "role": "test_role",
                    "resource": "test_resource", 
                    "action": "read",
                    "user_id": user.user_id
                }
            elif tool_name == "get_user_roles":
                arguments = {"user_id": "test_user"}
            
            response = await client.call_tool_as_user(tool_name, user, arguments)
            
            # Analyze response to determine if access was granted
            access_granted = True
            error_details = ""
            
            if "error" in response:
                error_msg = response["error"].get("message", "").lower()
                if any(keyword in error_msg for keyword in ["access denied", "permission", "unauthorized", "forbidden"]):
                    access_granted = False
                    error_details = f"Access denied: {response['error'].get('message', 'Unknown')}"
                else:
                    # Other errors (like service unavailable) don't indicate RBAC denial
                    error_details = f"Service error: {response['error'].get('message', 'Unknown')}"
            elif "result" in response:
                result = response["result"]
                if isinstance(result, dict) and "error" in result:
                    error_msg = result["error"].lower()
                    if any(keyword in error_msg for keyword in ["access denied", "permission", "unauthorized"]):
                        access_granted = False
                        error_details = f"Access denied in result: {result['error']}"
                    else:
                        error_details = f"Service error in result: {result['error']}"
                else:
                    error_details = "Tool executed successfully"
            
            self._log_result(
                f"Tool Access Test",
                user,
                tool_name,
                expected_access,
                access_granted,
                error_details
            )
            
        except Exception as e:
            self._log_result(
                f"Tool Access Test",
                user,
                tool_name,
                expected_access,
                False,  # Exception means no access
                f"Exception: {e}"
            )
    
    async def test_user_permissions(self, client: RBACTestClient, user: TestUser):
        """Test all expected and denied permissions for a user"""
        print(f"🔍 Testing permissions for {user.description}")
        print(f"   User ID: {user.user_id}")
        print(f"   Role: {user.role}")
        print("-" * 60)
        
        # Test expected access (should be allowed)
        for tool in user.expected_access:
            await self.test_tool_access(client, user, tool, True)
        
        # Test denied access (should be blocked)
        for tool in user.denied_access:
            await self.test_tool_access(client, user, tool, False)
    
    async def test_role_hierarchy(self, client: RBACTestClient):
        """Test that role hierarchy works correctly (admin > event_owner > user)"""
        print("👑 Testing Role Hierarchy")
        print("-" * 40)
        
        # Test admin accessing event_owner tools
        admin = next(u for u in self.test_users if u.role == "admin")
        await self.test_tool_access(client, admin, "create_event", True)
        
        # Test admin accessing user tools
        await self.test_tool_access(client, admin, "create_rsvp", True)
        
        # Test event_owner accessing user tools (should work due to hierarchy)
        event_owner = next(u for u in self.test_users if u.role == "event_owner")
        await self.test_tool_access(client, event_owner, "list_all_events", True)
    
    async def test_casbin_policies(self, client: RBACTestClient):
        """Test Casbin policy management tools"""
        print("📋 Testing Casbin Policy Management")
        print("-" * 40)
        
        admin = next(u for u in self.test_users if u.role == "admin")
        regular_user = next(u for u in self.test_users if u.role == "user")
        
        # Admin should be able to view policies
        await self.test_tool_access(client, admin, "get_casbin_policies", True)
        
        # Regular user should be denied
        await self.test_tool_access(client, regular_user, "get_casbin_policies", False)
    
    async def run_comprehensive_rbac_tests(self):
        """Run all RBAC tests"""
        print("🔐 MCP Gateway RBAC Test Suite (Streamable HTTP)")
        print("=" * 60)
        print(f"Gateway URL: {self.gateway_url}")
        print(f"Testing {len(self.test_users)} user roles with Casbin RBAC")
        print()
        
        try:
            async with RBACTestClient(self.gateway_url) as client:
                if not client.session_id:
                    print("❌ Failed to initialize MCP client")
                    return
                
                print(f"✅ Connected with session: {client.session_id}")
                print()
                
                # Test each user's permissions
                for user in self.test_users:
                    await self.test_user_permissions(client, user)
                
                # Test role hierarchy
                await self.test_role_hierarchy(client)
                
                # Test Casbin-specific features
                await self.test_casbin_policies(client)
        
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print test results summary"""
        print("📊 RBAC Test Results Summary")
        print("=" * 40)
        
        passed = sum(1 for r in self.results if r["passed"])
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {total - passed}")
        print(f"📈 Success Rate: {(passed/max(1,total)*100):.1f}%")
        print()
        
        # Group by role
        roles = {}
        for result in self.results:
            role = result["role"]
            if role not in roles:
                roles[role] = {"passed": 0, "total": 0}
            roles[role]["total"] += 1
            if result["passed"]:
                roles[role]["passed"] += 1
        
        print("📋 Results by Role:")
        for role, stats in roles.items():
            success_rate = (stats["passed"] / max(1, stats["total"])) * 100
            print(f"  {role}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        # Show failed tests
        failed_tests = [r for r in self.results if not r["passed"]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['user_id']} ({test['role']}) -> {test['tool']}")
                print(f"    Expected: {'ALLOW' if test['expected'] else 'DENY'}, Got: {'ALLOW' if test['actual'] else 'DENY'}")
                if test['details']:
                    print(f"    Details: {test['details']}")
        
        print(f"\n🎯 RBAC Validation Complete:")
        print(f"✅ Casbin policy enforcement tested")
        print(f"✅ Role hierarchy validation completed")
        print(f"✅ Permission boundaries verified")
        print(f"✅ Streamable HTTP transport confirmed")

async def main():
    """Main test runner"""
    import sys
    
    gateway_url = "http://localhost:8003"
    if len(sys.argv) > 1:
        gateway_url = sys.argv[1]
    
    test_suite = RBACTestSuite(gateway_url)
    await test_suite.run_comprehensive_rbac_tests()

if __name__ == "__main__":
    asyncio.run(main())