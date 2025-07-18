#!/usr/bin/env python3
"""Test script to demonstrate Casbin RBAC functionality in the MCP Gateway"""

import asyncio
from casbin_rbac import CasbinRBACMiddleware
from tlt.mcp_services.gateway.models import UserRole, AuthContext

async def test_casbin_rbac():
    """Test Casbin RBAC permissions"""
    print("🔐 Testing Casbin RBAC System")
    print("=" * 40)
    
    # Initialize Casbin RBAC
    rbac = CasbinRBACMiddleware()
    
    # Test users with different roles
    admin_user = AuthContext(
        user_id="admin_001",
        role=UserRole.ADMIN,
        event_permissions=[],
        metadata={}
    )
    
    event_owner = AuthContext(
        user_id="owner_001", 
        role=UserRole.EVENT_OWNER,
        event_permissions=["event_123"],
        metadata={}
    )
    
    regular_user = AuthContext(
        user_id="user_001",
        role=UserRole.USER,
        event_permissions=[],
        metadata={}
    )
    
    # Test different tool permissions
    test_cases = [
        # Tool name, user context, expected result
        ("create_event", admin_user, True),
        ("create_event", event_owner, True),
        ("create_event", regular_user, False),
        
        ("get_event", admin_user, True),
        ("get_event", event_owner, True),
        ("get_event", regular_user, True),
        
        ("create_rsvp", admin_user, True),
        ("create_rsvp", event_owner, True),
        ("create_rsvp", regular_user, True),
        
        ("get_event_rsvps", admin_user, True),
        ("get_event_rsvps", event_owner, True),
        ("get_event_rsvps", regular_user, True),
        
        ("add_casbin_policy", admin_user, True),
        ("add_casbin_policy", event_owner, False),
        ("add_casbin_policy", regular_user, False),
        
        ("get_casbin_policies", admin_user, True),
        ("get_casbin_policies", event_owner, False),
        ("get_casbin_policies", regular_user, False),
    ]
    
    print("📋 Permission Test Results:")
    print()
    
    for tool_name, user_context, expected in test_cases:
        result = rbac.check_permission(tool_name, user_context)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        role_name = user_context.role.value.upper()
        
        print(f"{status} {role_name:12} | {tool_name:20} | Expected: {expected:5} | Got: {result:5}")
    
    print()
    print("📊 Policy Information:")
    print(f"Total Policies: {len(rbac.get_policy())}")
    
    print("\n🔧 Policy Rules:")
    for i, policy in enumerate(rbac.get_policy(), 1):
        if len(policy) >= 3:
            role, resource, action = policy[0], policy[1], policy[2]
            print(f"  {i}. {role} can {action} on {resource}")
    
    print("\n👥 Role Hierarchy:")
    print("  admin > event_owner > user")
    
    print("\n🎯 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_casbin_rbac())