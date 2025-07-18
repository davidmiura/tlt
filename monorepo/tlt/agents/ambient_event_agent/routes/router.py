"""Router for ambient event agent graph"""

from typing import Literal
from loguru import logger
from tlt.agents.ambient_event_agent.state.state import AgentState, AgentStatus

def should_continue_monitoring(state: AgentState) -> Literal["event_monitor", "reasoning", "complete"]:
    """Determine if agent should continue monitoring or move to processing"""
    
    # Get current iteration count without incrementing (nodes handle this)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("config", {}).get("max_iterations", None)
    
    # Check for max iterations (testing mode)
    if max_iterations and iteration_count >= max_iterations:
        logger.info(f"Reached max iterations ({max_iterations}), completing")
        return "complete"
    
    # Check for potential infinite loop (too many event monitor cycles without progress)
    monitoring_cycles = state.get("monitoring_cycles", 0)
    if monitoring_cycles % 100 == 0:
        if monitoring_cycles > 500 and not state["pending_events"]:
            logger.warning(f"Potential infinite loop detected after {monitoring_cycles} monitoring cycles, completing cycle")
            return "complete"
    
    # If there are pending events, process them
    if state["pending_events"]:
        # Signal that we have events to process - let reasoning node handle the queue manipulation
        return "reasoning"
    
    # If agent is stopping, complete the cycle
    if state["status"] == AgentStatus.STOPPING:
        return "complete"
    
    # If there's an error, try to recover or complete
    if state["status"] == AgentStatus.ERROR:
        # Check if we should retry or give up - let event_monitor handle retry_count increment
        if state["retry_count"] < state["config"].get("max_retry_attempts", 3):
            return "event_monitor"  # Try again
        else:
            return "complete"  # Give up
    
    # For development/testing, complete after a few iterations if no events AND no pending events
    if state.get("debug_mode", False) and state["iteration_count"] > 3 and not state["pending_events"]:
        logger.info("Debug mode: completing after 3 iterations with no pending events")
        return "complete"
    
    # Read monitoring cycles counter without incrementing - let event_monitor handle increment
    monitoring_cycles = state.get("monitoring_cycles", 0)
    
    # If we're in initialization mode, complete after first check (but only if no pending events)
    if monitoring_cycles >= 1 and state.get("status") == AgentStatus.IDLE and not state["pending_events"]:
        logger.debug("Initialization complete - exiting to main loop")
        return "complete"
    
    # If we've done too many monitoring cycles without events, complete
    if monitoring_cycles > 10 and not state["pending_events"]:
        logger.info(f"Completed {monitoring_cycles} monitoring cycles without events")
        return "complete"
    
    # Continue monitoring
    return "event_monitor"

def should_execute_actions(state: AgentState) -> Literal["mcp_executor", "discord_interface", "event_monitor"]:
    """Determine what actions to execute after reasoning"""
    
    # If reasoning found no current event, go back to monitoring
    if state.get("processing_step") == "no_current_event":
        return "event_monitor"
    
    # Check if we have pending MCP requests from reasoning
    if state.get("pending_mcp_requests") and len(state["pending_mcp_requests"]) > 0:
        return "mcp_executor"
    
    # Check if we need to make MCP calls (legacy decision types)
    needs_mcp = False
    for decision in state["recent_decisions"][-3:]:  # Check last 3 decisions
        if decision.decision_type in ["update_event", "create_reminder", "fetch_data", "use_mcp_tool"]:
            needs_mcp = True
            break
    
    if needs_mcp:
        return "mcp_executor"
    
    # Check if we have pending Discord messages
    if state["pending_messages"]:
        return "discord_interface"
    
    # No actions needed, return to monitoring
    return "event_monitor"

def should_continue_after_mcp(state: AgentState) -> Literal["discord_interface", "event_monitor"]:
    """Determine next step after MCP execution"""
    
    # If there are pending Discord messages, send them
    if state["pending_messages"]:
        return "discord_interface"
    
    # Otherwise return to monitoring
    return "event_monitor"

def should_continue_after_discord(state: AgentState) -> Literal["event_monitor", "complete"]:
    """Determine next step after Discord operations"""
    
    # If agent is stopping, complete
    if state["status"] == AgentStatus.STOPPING:
        return "complete"
    
    # Return to monitoring
    return "event_monitor"

def route_initialization(state: AgentState) -> Literal["event_monitor", "complete"]:
    """Route after initialization"""
    
    if state["status"] == AgentStatus.ERROR:
        return "complete"
    
    return "event_monitor"