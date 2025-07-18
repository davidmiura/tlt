#!/usr/bin/env python3
"""Test script for CloudEvent processing in ambient event agent"""

import asyncio
import sys
import os
from datetime import datetime, timezone

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tlt.agents.ambient_event_agent.agent.agent import AmbientEventAgent
from tlt.agents.ambient_event_agent.state.state import IncomingEvent, EventTriggerType, MessagePriority, CloudEventContext

async def test_cloudevent_processing():
    """Test CloudEvent processing capabilities"""
    print("🧪 Testing CloudEvent Processing in Ambient Event Agent")
    print("=" * 60)
    
    # Create agent
    agent = AmbientEventAgent(
        openai_api_key="test-key",  # Use dummy key for testing
        agent_id="test_agent",
        debug_mode=True,
        config={"recursion_limit": 10, "max_iterations": 3}
    )
    
    try:
        # Initialize agent
        print("1. Initializing agent...")
        await agent.initialize()
        print("✅ Agent initialized successfully")
        
        # Test 1: Create Event CloudEvent
        print("\n2. Testing create_event CloudEvent...")
        create_event_cloudevent = {
            "id": "test-create-event-001",
            "type": "com.tlt.discord.create-event",
            "source": "discord://guild/123456789/channel/987654321",
            "subject": "create-event-user123",
            "time": datetime.now(timezone.utc).isoformat(),
            "data": {
                "event_data": {
                    "topic": "Test Event from CloudEvent",
                    "location": "Virtual Discord",
                    "time": "Tomorrow at 3 PM",
                    "message_id": "1234567890",
                    "thread_id": "0987654321",
                    "creator_id": "user123",
                    "guild_id": "123456789",
                    "channel_id": "987654321"
                },
                "interaction_data": {
                    "user_id": "user123",
                    "user_name": "TestUser",
                    "guild_id": "123456789",
                    "guild_name": "Test Guild",
                    "channel_id": "987654321",
                    "channel_name": "test-events",
                    "command": "create_event",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                "message_id": "1234567890",
                "metadata": {
                    "source": "discord_create_command"
                }
            }
        }
        
        # Create CloudEvent as IncomingEvent
        cloudevent_context = CloudEventContext(
            cloudevent_id=create_event_cloudevent["id"],
            cloudevent_type=create_event_cloudevent["type"],
            cloudevent_source=create_event_cloudevent["source"],
            cloudevent_subject=create_event_cloudevent["subject"],
            cloudevent_time=datetime.fromisoformat(create_event_cloudevent["time"].replace('Z', '+00:00')),
            data=create_event_cloudevent["data"]
        )
        
        cloudevent_event = IncomingEvent(
            trigger_type=EventTriggerType.CLOUDEVENT,
            priority=MessagePriority.HIGH,
            cloudevent_context=cloudevent_context,
            raw_data=create_event_cloudevent,
            metadata={"test": True, "cloudevent_type": "create-event"}
        )
        
        # Add event to agent
        agent.add_event(cloudevent_event)
        print("✅ CloudEvent added to agent queue")
        
        # Process events
        print("\n3. Processing events...")
        for i in range(3):
            print(f"   Processing cycle {i+1}...")
            await agent.run_single_cycle()
            
            # Check state
            state = agent.get_state()
            if state:
                print(f"   - Status: {state['status']}")
                print(f"   - Pending events: {len(state['pending_events'])}")
                print(f"   - Recent decisions: {len(state['recent_decisions'])}")
                print(f"   - Pending MCP requests: {len(state.get('pending_mcp_requests', []))}")
                print(f"   - Tool call history: {len(state.get('tool_call_history', []))}")
                
                # Show recent decisions
                if state['recent_decisions']:
                    latest_decision = state['recent_decisions'][-1]
                    print(f"   - Latest decision: {latest_decision.decision_type} (confidence: {latest_decision.confidence:.2f})")
                    print(f"   - Reasoning: {latest_decision.reasoning[:100]}...")
        
        print("✅ Event processing completed")
        
        # Test 2: Update Event CloudEvent
        print("\n4. Testing update_event CloudEvent...")
        update_event_cloudevent = {
            "id": "test-update-event-001", 
            "type": "com.tlt.discord.update-event",
            "source": "discord://guild/123456789/channel/987654321",
            "time": datetime.now(timezone.utc).isoformat(),
            "data": {
                "event_data": {
                    "topic": "Updated Test Event",
                    "location": "Updated Virtual Discord",
                    "time": "Tomorrow at 4 PM", 
                    "message_id": "1234567890",
                    "updated_by": "user123",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                },
                "interaction_data": {
                    "user_id": "user123",
                    "user_name": "TestUser",
                    "guild_id": "123456789",
                    "channel_id": "987654321",
                    "command": "update_event"
                }
            }
        }
        
        update_cloudevent_context = CloudEventContext(
            cloudevent_id=update_event_cloudevent["id"],
            cloudevent_type=update_event_cloudevent["type"], 
            cloudevent_source=update_event_cloudevent["source"],
            cloudevent_time=datetime.fromisoformat(update_event_cloudevent["time"].replace('Z', '+00:00')),
            data=update_event_cloudevent["data"]
        )
        
        update_event = IncomingEvent(
            trigger_type=EventTriggerType.CLOUDEVENT,
            priority=MessagePriority.NORMAL,
            cloudevent_context=update_cloudevent_context,
            raw_data=update_event_cloudevent,
            metadata={"test": True, "cloudevent_type": "update-event"}
        )
        
        agent.add_event(update_event)
        await agent.run_single_cycle()
        print("✅ Update CloudEvent processed")
        
        # Show final state
        print("\n5. Final agent state:")
        final_state = agent.get_state()
        if final_state:
            print(f"   - Total iterations: {final_state['iteration_count']}")
            print(f"   - Total decisions: {len(final_state['recent_decisions'])}")
            print(f"   - Total tool calls: {len(final_state.get('tool_call_history', []))}")
            print(f"   - Final status: {final_state['status']}")
            
            # Show decision types made
            decision_types = [d.decision_type for d in final_state['recent_decisions']]
            print(f"   - Decision types: {decision_types}")
            
            # Show MCP tool calls made
            tool_calls = [tc.get('tool', 'unknown') for tc in final_state.get('tool_call_history', [])]
            print(f"   - MCP tools called: {tool_calls}")
        
        print("\n🎉 CloudEvent processing test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(test_cloudevent_processing())