"""Main agent implementation using LangGraph"""

import asyncio
import pprint
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from loguru import logger

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from tlt.shared.models.agent_task import AgentTask
from tlt.agents.ambient_event_agent.state.state import AgentState, AgentStatus, create_initial_state
from tlt.agents.ambient_event_agent.nodes.initialization import InitializationNode
from tlt.agents.ambient_event_agent.nodes.event_monitor import EventMonitorNode
from tlt.agents.ambient_event_agent.nodes.reasoning import ReasoningNode
from tlt.agents.ambient_event_agent.nodes.mcp_executor import MCPExecutorNode
from tlt.agents.ambient_event_agent.nodes.discord_interface import DiscordInterfaceNode
from tlt.agents.ambient_event_agent.routes.router import (
    route_initialization, should_continue_monitoring, 
    should_execute_actions, should_continue_after_mcp,
    should_continue_after_discord
)

# Using loguru logger imported above

class AmbientEventAgent:
    """Ambient event agent using LangGraph for orchestration"""
    
    def __init__(self, openai_api_key: str, agent_id: str = None, debug_mode: bool = False, config: dict = None):
        self.agent_id = agent_id
        self.openai_api_key = openai_api_key
        self.debug_mode = debug_mode
        self.config = config or {}
        self.recursion_limit = self.config.get("recursion_limit", 500)
        
        # Initialize nodes
        self.initialization_node = InitializationNode()
        self.event_monitor_node = EventMonitorNode()
        self.reasoning_node = ReasoningNode(openai_api_key)
        self.mcp_executor_node = MCPExecutorNode()
        self.discord_interface_node = DiscordInterfaceNode()
        
        # State management
        self.checkpointer = MemorySaver()
        self.current_state = None
        
        # Create the graph
        self.graph = self._create_graph()
        
        logger.debug(f"Initialized AmbientEventAgent {self.agent_id}")
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state graph"""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("initialization", self.initialization_node.execute)
        graph.add_node("event_monitor", self.event_monitor_node.execute)
        graph.add_node("reasoning", self.reasoning_node.execute)
        graph.add_node("mcp_executor", self.mcp_executor_node.execute)
        graph.add_node("discord_interface", self.discord_interface_node.execute)
        
        # Set entry point
        graph.set_entry_point("initialization")
        
        # Add conditional edges
        graph.add_conditional_edges(
            "initialization",
            route_initialization,
            {
                "event_monitor": "event_monitor",
                "complete": END
            }
        )
        
        graph.add_conditional_edges(
            "event_monitor",
            should_continue_monitoring,
            {
                "event_monitor": "event_monitor",
                "reasoning": "reasoning",
                "complete": END
            }
        )
        
        graph.add_conditional_edges(
            "reasoning",
            should_execute_actions,
            {
                "mcp_executor": "mcp_executor",
                "discord_interface": "discord_interface",
                "event_monitor": "event_monitor"
            }
        )
        
        graph.add_conditional_edges(
            "mcp_executor",
            should_continue_after_mcp,
            {
                "discord_interface": "discord_interface",
                "event_monitor": "event_monitor"
            }
        )
        
        graph.add_conditional_edges(
            "discord_interface",
            should_continue_after_discord,
            {
                "event_monitor": "event_monitor",
                "complete": END
            }
        )
        
        # Compile the graph with higher recursion limit
        return graph.compile(
            checkpointer=self.checkpointer,
            debug=self.debug_mode
        )
    
    async def initialize(self) -> AgentState:
        """Initialize the agent state"""
        initial_state = create_initial_state(self.agent_id)
        initial_state["debug_mode"] = self.debug_mode
        # Merge config from constructor with default config
        initial_state["config"].update(self.config)
        
        logger.debug(f"Starting agent initialization for {self.agent_id} with recursion limit {self.recursion_limit}")
        
        # Run initialization through the graph
        config = {
            "configurable": {"thread_id": self.agent_id},
            "recursion_limit": self.recursion_limit
        }
        
        try:
            result = await self.graph.ainvoke(initial_state, config=config)
            logger.debug(f"Agent initialization completed successfully")
        except Exception as e:
            logger.error(f"Agent initialization failed: {e}")
            raise
        
        self.current_state = result
        return result
    
    async def run_single_cycle(self) -> AgentState:
        """Run a single processing cycle"""
        if not self.current_state:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        config = {
            "configurable": {"thread_id": self.agent_id},
            "recursion_limit": self.recursion_limit
        }
        
        # Continue from current state
        result = await self.graph.ainvoke(self.current_state, config=config)
        
        self.current_state = result
        return result
    
    async def run_continuous(self, max_iterations: int = None, sleep_interval: float = 5.0):
        """Run the agent continuously"""
        if not self.current_state:
            await self.initialize()
        
        iteration = 0
        
        logger.debug(f"Starting continuous operation for agent {self.agent_id}")
        
        try:
            while True:
                # Check iteration limit
                if max_iterations and iteration >= max_iterations:
                    logger.info(f"Reached max iterations ({max_iterations})")
                    break
                
                # Check if agent should stop
                if self.current_state["status"] == AgentStatus.STOPPING:
                    logger.info("Agent stopping requested")
                    break
                
                # Run a cycle
                try:
                    # Set max_iterations in state for router decision making
                    if self.current_state:
                        self.current_state["config"]["max_iterations"] = max_iterations
                    
                    # Run actual cycle
                    self.current_state = await self.run_single_cycle()
                    iteration += 1
                    
                    # Log periodic status and check for abandoned tasks
                    if max_iterations or iteration % 10 == 0:
                        self._log_status()
                        
                        # Check for abandoned AgentTasks every 10 iterations
                        if iteration % 50 == 0:
                            from tlt.agents.ambient_event_agent.state.state import check_and_log_abandoned_tasks
                            check_and_log_abandoned_tasks(self.current_state, logger, max_age_minutes=30)
                    
                    # Check if agent completed naturally
                    if self.current_state["status"] == AgentStatus.STOPPING:
                        logger.info("Agent completed cycle naturally")
                        break
                    
                except Exception as e:
                    logger.error(f"Error in processing cycle {iteration}: {e}")
                    if self.current_state:
                        self.current_state["status"] = AgentStatus.ERROR
                        self.current_state["error_history"].append({
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "error": str(e),
                            "iteration": iteration
                        })
                    
                    # Try to recover
                    await asyncio.sleep(sleep_interval * 2)  # Wait longer on error
                
                # Sleep between cycles (shorter for testing)
                if max_iterations:
                    await asyncio.sleep(0.1)  # Short sleep for testing
                else:
                    await asyncio.sleep(sleep_interval)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping agent")
            await self.stop()
        
        except Exception as e:
            logger.error(f"Critical error in continuous operation: {e}")
            raise
    
    async def stop(self):
        """Stop the agent gracefully"""
        if self.current_state:
            self.current_state["status"] = AgentStatus.STOPPING
            logger.info(f"Agent {self.agent_id} stopping")
    
    def _log_status(self):
        """Log current agent status"""
        if not self.current_state:
            return
        
        status_info = {
            "agent_id": self.agent_id,
            "status": self.current_state["status"],
            "iteration": self.current_state["iteration_count"],
            "pending_events": len(self.current_state["pending_events"]),
            "pending_messages": len(self.current_state["pending_messages"]),
            "active_timers": len(self.current_state["active_timers"]),
            "recent_decisions": len(self.current_state["recent_decisions"])
        }
        
        logger.info(f"Agent status: {status_info}")
    
    def get_state(self) -> Optional[AgentState]:
        """Get current agent state"""
        return self.current_state
    
    def add_event(self, event):
        """Add an external event to the agent's queue - accepts AgentTask, IncomingEvent, or dict"""
        if not self.current_state:
            raise ValueError("Agent not initialized")
        
        from tlt.agents.ambient_event_agent.state.state import (
            IncomingEvent, EventTriggerType, MessagePriority, 
            track_agent_task_lifecycle, AgentTaskLifecycleStatus, check_and_log_abandoned_tasks
        )
        
        # Log entry point for all events/AgentTasks
        logger.info(f"Agent: add_event called with event type={type(event)}, data={getattr(event, '__dict__', event)}")
        
        # Handle IncomingEvent directly
        if isinstance(event, IncomingEvent):
            incoming_event = event
            logger.info(f"Agent: Added IncomingEvent directly: {incoming_event.event_id} ({incoming_event.trigger_type})")
        
        # Handle AgentTask
        elif isinstance(event, AgentTask):
            # Log AgentTask details before conversion
            logger.info(f"Agent: Processing AgentTask - task_id={event.task_id}, event_id={event.event_id}, trigger_type={event.trigger_type}, data={event.data}")
            
            # Track AgentTask lifecycle - RECEIVED
            track_agent_task_lifecycle(
                self.current_state,
                task_id=event.task_id,
                event_id=event.event_id,
                status=AgentTaskLifecycleStatus.RECEIVED,
                details=f"AgentTask received by agent, trigger_type={event.trigger_type}",
                agent_task_type=event.trigger_type.value,
                cloudevent_type=event.data.get("cloudevent", {}).get("type") if isinstance(event.data, dict) else None,
                metadata={"raw_data": event.data}
            )
            
            # Map AgentTask trigger type to ambient agent trigger type
            trigger_type_mapping = {
                "cloudevent": EventTriggerType.MANUAL_TRIGGER,
                "discord_message": EventTriggerType.DISCORD_MESSAGE,
                "timer_trigger": EventTriggerType.TIMER_TRIGGER,
                "create_event": EventTriggerType.CREATE_EVENT,
            }
            mapped_trigger_type = trigger_type_mapping.get(
                event.trigger_type.value, 
                EventTriggerType.MANUAL_TRIGGER
            )
            
            # Convert AgentTask directly to IncomingEvent
            incoming_event = IncomingEvent(
                event_id=event.event_id,
                trigger_type=mapped_trigger_type,
                priority=event.message_priority,
                timestamp=event.timestamp,
                discord_context=event.discord_context,
                timer_context=event.timer_context,
                event_context=event.event_context,
                raw_data=event.data,
                metadata=event.metadata
            )
            logger.info(f"Agent: AgentTask converted to IncomingEvent - task_id={event.task_id}, mapped_trigger_type={mapped_trigger_type}, raw_data={event.data}")
            
            # Track AgentTask lifecycle - QUEUED
            track_agent_task_lifecycle(
                self.current_state,
                task_id=event.task_id,
                event_id=event.event_id,
                status=AgentTaskLifecycleStatus.QUEUED,
                details=f"Converted to IncomingEvent and queued for processing",
                metadata={"mapped_trigger_type": mapped_trigger_type.value}
            )
        
        # Handle dict (legacy)
        elif isinstance(event, dict):
            incoming_event = IncomingEvent(
                trigger_type=EventTriggerType(event.get("trigger_type", "manual_trigger")),
                priority=MessagePriority(event.get("priority", "normal")),
                raw_data=event.get("data", {}),
                metadata=event.get("metadata", {})
            )
            logger.info(f"Added dict event: {incoming_event.trigger_type}")
        
        else:
            raise ValueError(f"Unsupported event type: {type(event)}")
        
        logger.info(f"incoming_event: {pprint.pformat(incoming_event.model_dump(), indent=2, compact=False)}")
        self.current_state["pending_events"].append(incoming_event)
        logger.info(f"Event added to pending queue: {incoming_event.event_id}")
    
    def schedule_timer(self, event_id: str, timer_type: str, scheduled_time: datetime, priority: str = "normal"):
        """Schedule a timer for the agent"""
        if not self.current_state:
            raise ValueError("Agent not initialized")
        
        from tlt.agents.ambient_event_agent.state.state import ScheduledTimer, MessagePriority
        
        timer = ScheduledTimer(
            event_id=event_id,
            timer_type=timer_type,
            scheduled_time=scheduled_time,
            priority=MessagePriority(priority)
        )
        
        self.current_state["active_timers"].append(timer)
        logger.info(f"Scheduled {timer_type} timer for event {event_id} at {scheduled_time}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        if not self.current_state:
            return {}
        
        return {
            "uptime_seconds": (datetime.now(timezone.utc) - self.current_state["started_at"]).total_seconds(),
            "iterations": self.current_state["iteration_count"],
            "events_processed": len(self.current_state["processed_events"]),
            "decisions_made": len(self.current_state["recent_decisions"]),
            "messages_sent": len([h for h in self.current_state["tool_call_history"] if "discord" in h.get("service", "")]),
            "errors": len(self.current_state["error_history"]),
            "active_timers": len(self.current_state["active_timers"]),
            "cached_events": len(self.current_state["event_cache"])
        }