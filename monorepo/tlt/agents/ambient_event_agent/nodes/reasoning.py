"""Reasoning node for ambient event agent"""

import json
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from pydantic import BaseModel, Field

from loguru import logger

from tlt.agents.ambient_event_agent.nodes.base import BaseNode
from tlt.agents.ambient_event_agent.state.state import (
    AgentState, AgentStatus, IncomingEvent, AgentDecision,
    MessageToSend, MessagePriority, ScheduledTimer,
    track_agent_task_lifecycle, AgentTaskLifecycleStatus, get_agent_task_provenance
)

class AgentReasoningDecision(BaseModel):
    """Make a reasoning decision for the ambient event agent based on the current context.
    
    This tool analyzes the current event and decides what action the agent should take.
    The agent can send messages, schedule timers, use MCP tools, or take no action.
    """
    
    decision_type: str = Field(
        description="Type of decision to make. Must be one of: send_message, schedule_timer, use_mcp_tool, no_action, update_event, create_reminder"
    )
    reasoning: str = Field(
        description="Detailed reasoning for why this decision was made, including analysis of the context and expected outcomes"
    )
    confidence: float = Field(
        ge=0.0, le=1.0, 
        description="Confidence level in this decision from 0.0 to 1.0"
    )
    
    # Message sending fields
    message_content: Optional[str] = Field(
        None, 
        description="Content of the message to send (required if decision_type is send_message)"
    )
    channel_id: Optional[str] = Field(
        None,
        description="Discord channel ID to send the message to (required if decision_type is send_message)"
    )
    
    # Timer scheduling fields
    timer_type: Optional[str] = Field(
        None,
        description="Type of timer to schedule (required if decision_type is schedule_timer)"
    )
    timer_delay_minutes: Optional[int] = Field(
        None,
        description="Minutes to delay before timer triggers (required if decision_type is schedule_timer)"
    )
    
    # MCP tool execution fields
    mcp_tool_name: Optional[str] = Field(
        None,
        description="Name of the MCP tool to use (required if decision_type is use_mcp_tool)"
    )
    mcp_tool_args: Optional[Dict[str, Any]] = Field(
        None,
        description="Arguments to pass to the MCP tool (required if decision_type is use_mcp_tool)"
    )
    
    # Common fields
    priority: str = Field(
        default="normal",
        description="Priority level for the action: low, normal, high, urgent"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata for the action"
    )

class ReasoningNode(BaseNode):
    """Use LLM reasoning to decide what action to take"""
    
    def __init__(self, openai_api_key: str):
        super().__init__("reasoning")
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o-mini",
            temperature=0.3,
            max_tokens=1000
        )
        # Bind the tool schema to the LLM for structured output
        self.llm_with_tools = self.llm.bind_tools([AgentReasoningDecision])
        self.parser = PydanticToolsParser(tools=[AgentReasoningDecision])
        
        # Create the chain for tool calling
        self.reasoning_chain = self.llm_with_tools | self.parser
    
    async def execute(self, state: AgentState) -> AgentState:
        """Analyze current event and decide on actions"""
        self.log_execution(state, "Starting reasoning process")
        
        # Track all current processing tasks entering reasoning
        for task_id in state.get("current_processing_tasks", []):
            # Find the event_id for this task
            lifecycle = state.get("agent_task_lifecycles", {}).get(task_id)
            if lifecycle:
                track_agent_task_lifecycle(
                    state,
                    task_id=task_id,
                    event_id=lifecycle.event_id,
                    status=AgentTaskLifecycleStatus.REASONING,
                    node_name="reasoning",
                    details="Entering reasoning node for decision making"
                )
                logger.info(f"Reasoning: Tracking AgentTask {task_id} in reasoning node")
        
        try:
            self.update_state_metadata(state, {
                "status": AgentStatus.PROCESSING,
                "processing_step": "reasoning"
            })
            
            # Handle pending events queue (moved from router)
            if state["pending_events"] and not state.get("current_event"):
                # Get the next event to process
                next_event = state["pending_events"].pop(0)
                state["current_event"] = next_event
                # Mark event as processed
                state["processed_events"].append(next_event.event_id)
                self.log_execution(state, f"Processing event {next_event.event_id} from queue")
            
            current_event = state["current_event"]
            if not current_event:
                self.log_execution(state, "No current event to reason about")
                self.update_state_metadata(state, {
                    "processing_step": "no_current_event",
                    "current_event": None
                })
                return state
            
            # Find associated AgentTask for this event
            current_task_id = None
            for task_id, lifecycle in state.get("agent_task_lifecycles", {}).items():
                if lifecycle.event_id == current_event.event_id:
                    current_task_id = task_id
                    break
            
            # Log reasoning context for AgentTask
            if current_task_id:
                track_agent_task_lifecycle(
                    state,
                    task_id=current_task_id,
                    event_id=current_event.event_id,
                    status=AgentTaskLifecycleStatus.PROCESSING,
                    node_name="reasoning",
                    details=f"Building reasoning context for event {current_event.trigger_type}",
                    metadata={"event_trigger_type": current_event.trigger_type.value}
                )
                logger.info(f"Reasoning: Building context for AgentTask {current_task_id}")
            
            # Build context for reasoning
            context = await self._build_reasoning_context(state, current_event)
            
            # Log LLM decision request
            if current_task_id:
                track_agent_task_lifecycle(
                    state,
                    task_id=current_task_id,
                    event_id=current_event.event_id,
                    status=AgentTaskLifecycleStatus.PROCESSING,
                    node_name="reasoning",
                    details="Requesting LLM decision for event processing",
                    metadata={"has_cloudevent_context": current_event.cloudevent_context is not None}
                )
                logger.info(f"Reasoning: Requesting LLM decision for AgentTask {current_task_id}")
            
            # Get LLM decision
            decision_output = await self._get_llm_decision(state, context)
            
            # Process the decision
            decision = AgentDecision(
                decision_type=decision_output.decision_type,
                reasoning=decision_output.reasoning,
                confidence=decision_output.confidence,
                metadata=decision_output.metadata
            )
            
            state["recent_decisions"].append(decision)
            
            # Log decision made
            if current_task_id:
                track_agent_task_lifecycle(
                    state,
                    task_id=current_task_id,
                    event_id=current_event.event_id,
                    status=AgentTaskLifecycleStatus.PROCESSING,
                    node_name="reasoning",
                    details=f"LLM decision made: {decision.decision_type} (confidence: {decision.confidence:.2f})",
                    metadata={
                        "decision_type": decision.decision_type,
                        "confidence": decision.confidence,
                        "reasoning_snippet": decision.reasoning[:100] + "..." if len(decision.reasoning) > 100 else decision.reasoning
                    }
                )
                logger.info(f"Reasoning: Decision made for AgentTask {current_task_id}: {decision.decision_type}")
            
            # Execute the decision
            await self._execute_decision(state, decision_output, current_task_id)
            
            self.update_state_metadata(state, {
                "processing_step": "decision_made",
                "current_event": None  # Clear current event after processing
            })
            
            self.log_execution(state, f"Decision made: {decision.decision_type} (confidence: {decision.confidence:.2f})")
            
        except Exception as e:
            self.handle_error(state, e, "reasoning")
            state["status"] = AgentStatus.ERROR
        
        return state
    
    async def _build_reasoning_context(self, state: AgentState, event: IncomingEvent) -> Dict[str, Any]:
        """Build context information for LLM reasoning"""
        context = {
            "current_time": datetime.now(timezone.utc).isoformat(),
            "agent_status": state["status"],
            "event": {
                "trigger_type": event.trigger_type,
                "priority": event.priority,
                "timestamp": event.timestamp.isoformat(),
                "metadata": event.metadata
            },
            "recent_activity": {
                "recent_decisions": [
                    {
                        "type": d.decision_type,
                        "reasoning": d.reasoning,
                        "confidence": d.confidence,
                        "timestamp": d.timestamp.isoformat()
                    }
                    for d in state["recent_decisions"][-5:]  # Last 5 decisions
                ],
                "pending_messages": len(state["pending_messages"]),
                "active_timers": len(state["active_timers"]),
                "pending_mcp_requests": len(state.get("pending_mcp_requests", []))
            },
            "mcp_capabilities": {
                "available_tools": state.get("available_tools", []),
                "recent_tool_calls": state.get("tool_call_history", [])[-3:]  # Last 3 tool calls
            }
        }
        
        # Add CloudEvent context if available
        if event.cloudevent_context:
            context["cloudevent"] = {
                "type": event.cloudevent_context.cloudevent_type,
                "source": event.cloudevent_context.cloudevent_source,
                "id": event.cloudevent_context.cloudevent_id,
                "subject": event.cloudevent_context.cloudevent_subject,
                "time": event.cloudevent_context.cloudevent_time.isoformat() if event.cloudevent_context.cloudevent_time else None,
                "data": event.cloudevent_context.data
            }
            
            # Add CloudEvent-specific analysis
            context["cloudevent_analysis"] = self._analyze_cloudevent_for_mcp(event.cloudevent_context)
        
        # Add specific context based on trigger type
        if event.discord_context:
            context["discord"] = {
                "channel_id": event.discord_context.channel_id,
                "user_id": event.discord_context.user_id,
                "message_id": event.discord_context.message_id,
                "guild_id": event.discord_context.guild_id,
                "raw_data": event.raw_data
            }
        
        if event.timer_context:
            context["timer"] = {
                "timer_type": event.timer_context.timer_type,
                "event_id": event.timer_context.event_id,
                "scheduled_time": event.timer_context.scheduled_time.isoformat()
            }
            
            # Add event context if available
            if event.timer_context.event_id in state["event_cache"]:
                event_ctx = state["event_cache"][event.timer_context.event_id]
                context["event_info"] = {
                    "title": event_ctx.event_title,
                    "description": event_ctx.event_description,
                    "start_time": event_ctx.start_time.isoformat() if event_ctx.start_time else None,
                    "location": event_ctx.location,
                    "rsvp_count": event_ctx.rsvp_count,
                    "emoji_summary": event_ctx.emoji_summary
                }
        
        return context
    
    async def _get_llm_decision(self, state: AgentState, context: Dict[str, Any]) -> AgentReasoningDecision:
        """Get decision from LLM"""
        system_prompt = """You are an ambient event agent for event management. Your role is to:

1. Monitor events and timers
2. Send helpful, contextual messages to Discord channels
3. Schedule appropriate follow-up actions
4. Use MCP tools to interact with backend services
5. Provide value without being spammy

Consider the context provided and decide on the best action. You can:
- Send a message to a Discord channel
- Schedule a timer for future action
- Use MCP tools to perform backend operations
- Take no action if not appropriate

Be thoughtful about timing, relevance, and user experience. Focus on being helpful rather than noisy.

Available decision types:
- send_message: Send a message to Discord
- schedule_timer: Schedule a future timer
- use_mcp_tool: Use an MCP tool to perform actions (RECOMMENDED for most CloudEvents)
- no_action: Do nothing
- update_event: Update event information
- create_reminder: Create a reminder for users

Available MCP tools and their use cases:
- event_manager: Create, update, delete, and manage events
  - Use for: create_event, update_event, delete_event triggers
- rsvp: Manage RSVPs for events
  - Use for: RSVP-related operations
- photo_vibe_check: Handle photo submissions and processing
  - Use for: Photo-related events
- vibe_bit: Manage collaborative canvas
  - Use for: Canvas and collaborative activities

CloudEvent Processing Guidelines:
- For CloudEvents from Discord commands, typically use 'use_mcp_tool'
- CloudEvent types like 'com.tlt.discord.create-event' should use event_manager MCP tool
- Guild registration/deregistration events may just need logging (no_action)
- Info/list requests may not need MCP calls (no_action or send_message)

Consider message priority (low, normal, high, urgent) based on importance and timing."""

        # Create a JSON-safe version of context for serialization
        def make_json_safe(obj):
            """Convert objects to JSON-safe representations"""
            if hasattr(obj, '__dict__'):
                return str(obj)
            elif isinstance(obj, dict):
                return {k: make_json_safe(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_safe(item) for item in obj]
            elif isinstance(obj, (str, int, float, bool, type(None))):
                return obj
            else:
                return str(obj)
        
        json_safe_context = make_json_safe(context)
        
        user_prompt = f"""Current context:
{json.dumps(json_safe_context, indent=2)}

Based on this context, analyze the situation and use the AgentReasoningDecision tool to make an appropriate decision.

Consider:
1. The type of trigger (timer, Discord message, CloudEvent, etc.)
2. Recent agent activity to avoid spam
3. The appropriateness of the timing
4. The value to users
5. Whether an MCP tool call is needed based on the event type

CloudEvent Processing Guidelines:
- For CloudEvent triggers, analyze the cloudevent_analysis section
- If recommended_mcp_tool is provided, use that tool
- If requires_mcp_action is true, use 'use_mcp_tool' decision type
- Pass the CloudEvent data to the appropriate MCP tool

Special handling for specific trigger types:
- CLOUDEVENT_CREATE_EVENT: Use event_manager MCP tool to create the event
- CLOUDEVENT_UPDATE_EVENT: Use event_manager MCP tool to update the event
- CLOUDEVENT_DELETE_EVENT: Use event_manager MCP tool to delete the event
- CLOUDEVENT_RSVP_EVENT: Use rsvp MCP tool to process RSVP reactions and determine attendance
- CLOUDEVENT_REGISTER_GUILD: Use guild_manager MCP tool to register the guild
- CLOUDEVENT_DEREGISTER_GUILD: Use guild_manager MCP tool to deregister the guild
- CLOUDEVENT_LIST_EVENTS: Use event_manager MCP tool to fetch current events data
- CLOUDEVENT_EVENT_INFO: Usually no MCP action needed unless analytics update is required

Use the AgentReasoningDecision tool to provide your structured decision."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # Log messages safely without potential serialization issues
        logger.info(f'LLM Request: {len(messages)} messages sent to reasoning LLM with tool calling')
        
        try:
            # Use the reasoning chain for structured output
            logger.debug("Invoking reasoning chain...")
            parsed_decisions = await self.reasoning_chain.ainvoke(messages)
            logger.debug(f"Reasoning chain returned: {type(parsed_decisions)}, length: {len(parsed_decisions) if parsed_decisions else 0}")
            
            # Extract the first (and should be only) decision
            if parsed_decisions and len(parsed_decisions) > 0:
                decision = parsed_decisions[0]
                logger.info(f"Reasoning decision: {decision.decision_type} (confidence: {decision.confidence})")
                logger.debug(f"Decision reasoning: {decision.reasoning}")
            else:
                # Fallback if no tool call was made
                logger.warning("No tool call in LLM response, creating default no_action decision")
                decision = AgentReasoningDecision(
                    decision_type="no_action",
                    reasoning="LLM did not make a tool call, defaulting to no action",
                    confidence=0.1
                )
            
            return decision
            
        except Exception as e:
            logger.error(f"Error in reasoning chain: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Fallback decision on error
            return AgentReasoningDecision(
                decision_type="no_action",
                reasoning=f"Error in reasoning chain: {str(e)}",
                confidence=0.1
            )
    
    async def _execute_decision(self, state: AgentState, decision: AgentReasoningDecision, task_id: Optional[str] = None):
        """Execute the decision made by the LLM"""
        if decision.decision_type == "send_message":
            if decision.message_content and decision.channel_id:
                message = MessageToSend(
                    channel_id=decision.channel_id,
                    content=decision.message_content,
                    priority=MessagePriority(decision.priority),
                    metadata=decision.metadata
                )
                state["pending_messages"].append(message)
                self.log_execution(state, f"Queued message for channel {decision.channel_id}")
                
                # Track decision execution
                if task_id:
                    track_agent_task_lifecycle(
                        state,
                        task_id=task_id,
                        event_id=state["current_event"].event_id if state["current_event"] else "unknown",
                        status=AgentTaskLifecycleStatus.PROCESSING,
                        node_name="reasoning",
                        details=f"Decision executed: queued message for Discord channel {decision.channel_id}",
                        metadata={"decision_type": "send_message", "channel_id": decision.channel_id}
                    )
        
        elif decision.decision_type == "schedule_timer":
            if decision.timer_type and decision.timer_delay_minutes:
                from datetime import timedelta
                scheduled_time = datetime.now(timezone.utc) + timedelta(minutes=decision.timer_delay_minutes)
                
                timer = ScheduledTimer(
                    event_id=state["current_event"].timer_context.event_id if state["current_event"].timer_context else "unknown",
                    timer_type=decision.timer_type,
                    scheduled_time=scheduled_time,
                    priority=MessagePriority(decision.priority),
                    metadata=decision.metadata
                )
                state["active_timers"].append(timer)
                self.log_execution(state, f"Scheduled {decision.timer_type} timer for {scheduled_time}")
        
        elif decision.decision_type == "use_mcp_tool":
            if decision.mcp_tool_name:
                # Get current event for context
                current_event = state["current_event"]
                
                # Track MCP tool decision
                if task_id:
                    track_agent_task_lifecycle(
                        state,
                        task_id=task_id,
                        event_id=current_event.event_id if current_event else "unknown",
                        status=AgentTaskLifecycleStatus.PROCESSING,
                        node_name="reasoning",
                        details=f"Decision executed: preparing MCP tool request for {decision.mcp_tool_name}",
                        metadata={"decision_type": "use_mcp_tool", "mcp_tool_name": decision.mcp_tool_name}
                    )
                
                # Prepare MCP tool arguments, incorporating CloudEvent analysis if available
                mcp_args = decision.mcp_tool_args or {}
                tool_name = decision.mcp_tool_name
                
                # If we have CloudEvent context, use the analyzed arguments and tool name
                if (current_event and current_event.cloudevent_context and 
                    hasattr(current_event, 'cloudevent_context')):
                    
                    cloudevent_analysis = self._analyze_cloudevent_for_mcp(current_event.cloudevent_context)
                    if cloudevent_analysis.get("mcp_tool_args"):
                        mcp_args = cloudevent_analysis["mcp_tool_args"]  # Replace, don't update, to avoid extra args
                    if cloudevent_analysis.get("recommended_tool_name"):
                        tool_name = cloudevent_analysis["recommended_tool_name"]
                
                # Store MCP tool request in state for mcp_executor node
                mcp_request = {
                    "tool_name": tool_name,
                    "arguments": mcp_args,
                    "priority": decision.priority,
                    "metadata": {
                        **decision.metadata,
                        "cloudevent_id": current_event.cloudevent_context.cloudevent_id if (current_event and current_event.cloudevent_context) else None,
                        "cloudevent_type": current_event.cloudevent_context.cloudevent_type if (current_event and current_event.cloudevent_context) else None,
                        "associated_task_id": task_id  # Track the original AgentTask
                    },
                    "event_id": current_event.event_id if current_event else None
                }
                
                # Add to pending MCP requests
                if "pending_mcp_requests" not in state:
                    state["pending_mcp_requests"] = []
                state["pending_mcp_requests"].append(mcp_request)
                
                self.log_execution(state, f"Queued MCP tool request: {tool_name} with enhanced CloudEvent context")
                
                # Track MCP request queued
                if task_id:
                    track_agent_task_lifecycle(
                        state,
                        task_id=task_id,
                        event_id=current_event.event_id if current_event else "unknown",
                        status=AgentTaskLifecycleStatus.PROCESSING,
                        node_name="reasoning",
                        details=f"MCP tool request queued for {tool_name}, will be executed by mcp_executor node",
                        metadata={
                            "mcp_tool_name": tool_name,
                            "mcp_args_keys": list(mcp_args.keys()),
                            "has_cloudevent_context": current_event.cloudevent_context is not None
                        }
                    )
                
                # Set processing step to indicate MCP execution needed
                state["processing_step"] = "mcp_execution_needed"
        
        elif decision.decision_type == "no_action":
            self.log_execution(state, f"No action taken: {decision.reasoning}")
            
            # Track no_action decision 
            if task_id:
                track_agent_task_lifecycle(
                    state,
                    task_id=task_id,
                    event_id=state["current_event"].event_id if state["current_event"] else "unknown",
                    status=AgentTaskLifecycleStatus.PROCESSING,
                    node_name="reasoning",
                    details=f"Decision executed: no_action - {decision.reasoning[:100]}...",
                    metadata={"decision_type": "no_action", "reasoning_snippet": decision.reasoning[:200]}
                )
        
        # Limit list sizes
        if len(state["recent_decisions"]) > 20:
            state["recent_decisions"] = state["recent_decisions"][-10:]
    
    def _analyze_cloudevent_for_mcp(self, cloudevent_context) -> Dict[str, Any]:
        """Analyze CloudEvent to determine if MCP tool calls are needed"""
        analysis = {
            "requires_mcp_action": False,
            "recommended_mcp_tool": None,
            "recommended_action": "no_action",
            "confidence": 0.5,
            "reasoning": "Default analysis"
        }
        
        cloudevent_type = cloudevent_context.cloudevent_type
        cloudevent_data = cloudevent_context.data
        
        # Analysis for different CloudEvent types
        if cloudevent_type == "com.tlt.discord.create-event":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "event_manager",
                "recommended_action": "create_event",
                "confidence": 0.9,
                "reasoning": "Event creation requires MCP event_manager tool to persist event data",
                "mcp_tool_args": {
                    "action": "create_event",
                    "event_data": cloudevent_data.get("event_data", {}),
                    "interaction_data": cloudevent_data.get("interaction_data", {}),
                    "metadata": cloudevent_data.get("metadata", {})
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.save-event-to-guild-data":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "event_manager",
                "recommended_action": "save_event_to_guild_data",
                "confidence": 0.9,
                "reasoning": "Save event to guild_data requires MCP event_manager tool to persist event data to file system",
                "mcp_tool_args": {
                    "action": "save_event_to_guild_data",
                    "event_id": cloudevent_data.get("event_id"),
                    "guild_id": cloudevent_data.get("guild_id"),
                    "event_data": cloudevent_data.get("event_data", {}),
                    "metadata": cloudevent_data.get("metadata", {})
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.update-event":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "event_manager",
                "recommended_action": "update_event",
                "confidence": 0.9,
                "reasoning": "Event update requires MCP event_manager tool to update persistent data",
                "mcp_tool_args": {
                    "action": "update_event",
                    "event_data": cloudevent_data.get("event_data", {}),
                    "interaction_data": cloudevent_data.get("interaction_data", {}),
                    "metadata": cloudevent_data.get("metadata", {})
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.delete-event":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "event_manager",
                "recommended_action": "delete_event",
                "confidence": 0.9,
                "reasoning": "Event deletion requires MCP event_manager tool to remove from persistent storage",
                "mcp_tool_args": {
                    "action": "delete_event",
                    "event_id": cloudevent_data.get("event_id"),
                    "interaction_data": cloudevent_data.get("interaction_data", {}),
                    "metadata": cloudevent_data.get("metadata", {})
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.register-guild":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "guild_manager",
                "recommended_action": "register_guild",
                "confidence": 0.9,
                "reasoning": "Guild registration requires MCP guild_manager tool to persist guild registration",
                "mcp_tool_args": {
                    "action": "register_guild",
                    "guild_id": cloudevent_data.get("guild_id"),
                    "guild_name": cloudevent_data.get("guild_name"),
                    "channel_id": cloudevent_data.get("channel_id"),
                    "channel_name": cloudevent_data.get("channel_name"),
                    "user_id": cloudevent_data.get("user_id"),
                    "user_name": cloudevent_data.get("user_name"),
                    "metadata": cloudevent_data.get("metadata", {})
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.deregister-guild":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "guild_manager",
                "recommended_action": "deregister_guild",
                "confidence": 0.9,
                "reasoning": "Guild deregistration requires MCP guild_manager tool to remove guild registration",
                "mcp_tool_args": {
                    "action": "deregister_guild",
                    "guild_id": cloudevent_data.get("guild_id"),
                    "guild_name": cloudevent_data.get("guild_name"),
                    "user_id": cloudevent_data.get("user_id"),
                    "user_name": cloudevent_data.get("user_name"),
                    "metadata": cloudevent_data.get("metadata", {})
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.list-events":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "event_manager",
                "recommended_action": "list_all_events",
                "confidence": 0.8,
                "reasoning": "List events request should use MCP event_manager tool to fetch current events data",
                "mcp_tool_args": {
                    "action": "list_all_events",
                    "status": None,  # Get all events regardless of status
                    "limit": 100     # Default limit
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.event-info":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": None,
                "recommended_action": "log_activity",
                "confidence": 0.7,
                "reasoning": "Event info requests are read-only operations that don't require MCP actions"
            })
        
        elif cloudevent_type == "com.tlt.discord.rsvp-event":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "rsvp",
                "recommended_action": "process_rsvp",
                "confidence": 0.9,
                "reasoning": "RSVP event requires MCP rsvp tool to process reaction and determine attendance",
                "mcp_tool_args": {
                    "action": "process_rsvp",
                    "event_id": cloudevent_data.get("event_id"),
                    "user_id": cloudevent_data.get("user_id"),
                    "rsvp_type": cloudevent_data.get("rsvp_type"),
                    "emoji": cloudevent_data.get("emoji"),
                    "metadata": cloudevent_data.get("metadata", {})
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.message":
            # Analyze message content to determine if action needed
            message_content = cloudevent_data.get("content", "")
            if any(keyword in message_content.lower() for keyword in ["event", "rsvp", "reminder"]):
                analysis.update({
                    "requires_mcp_action": True,
                    "recommended_mcp_tool": "event_manager",
                    "recommended_action": "analyze_message",
                    "confidence": 0.6,
                    "reasoning": "Discord message contains event-related keywords that may require processing"
                })
            else:
                analysis.update({
                    "requires_mcp_action": False,
                    "recommended_action": "monitor_only",
                    "confidence": 0.8,
                    "reasoning": "Discord message doesn't contain event-related content"
                })
        
        elif cloudevent_type == "com.tlt.discord.photo-vibe-check":
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "photo_vibe_check",
                "recommended_action": "submit_photo_dm",
                "confidence": 0.9,
                "reasoning": "Photo vibe check submission requires MCP photo_vibe_check tool to process photo",
                "mcp_tool_args": {
                    "action": "submit_photo_dm",
                    "event_id": cloudevent_data.get("event_id"),
                    "user_id": cloudevent_data.get("user_id"),
                    "photo_url": cloudevent_data.get("photo_url"),
                    "metadata": {
                        "filename": cloudevent_data.get("filename"),
                        "content_type": cloudevent_data.get("content_type"),
                        "size": cloudevent_data.get("size"),
                        "message_content": cloudevent_data.get("message_content"),
                        "guild_id": cloudevent_data.get("guild_id"),
                        "channel_id": cloudevent_data.get("channel_id"),
                        **cloudevent_data.get("metadata", {})
                    }
                }
            })
        
        elif cloudevent_type == "com.tlt.discord.vibe-action":
            action = cloudevent_data.get("action", "unknown")
            event_id = cloudevent_data.get("event_id")
            
            # Determine which MCP tool to call and build correct tool args
            if action == "generate_event_slideshow":
                mcp_tool_name = "generate_event_slideshow"
                mcp_service = "photo_vibe_check"
                tool_args = {"event_id": event_id}
            elif action == "get_event_photo_summary":
                mcp_tool_name = "get_event_photo_summary"
                mcp_service = "photo_vibe_check" 
                tool_args = {"event_id": event_id}
            elif action == "get_vibe_canvas_preview":
                mcp_tool_name = "get_vibe_canvas_preview"
                mcp_service = "vibe_bit"
                tool_args = {"event_id": event_id, "max_size": 512}
            elif action == "create_vibe_snapshot":
                mcp_tool_name = "create_vibe_snapshot"
                mcp_service = "vibe_bit"  # Fixed: create_vibe_snapshot is in vibe_bit, not event_manager
                tool_args = {"event_id": event_id, "snapshot_type": "progress"}
            else:
                mcp_tool_name = "get_event_photo_summary"  # Default fallback
                mcp_service = "photo_vibe_check"
                tool_args = {"event_id": event_id}
            
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": mcp_service,
                "recommended_tool_name": mcp_tool_name,
                "recommended_action": action,
                "confidence": 0.9,
                "reasoning": f"Vibe action '{action}' requires MCP {mcp_service}/{mcp_tool_name} tool to process request",
                "mcp_tool_args": tool_args
            })
        
        elif cloudevent_type == "com.tlt.discord.promotion-image":
            event_id = cloudevent_data.get("event_id")
            image_url = cloudevent_data.get("image_url")
            local_path = cloudevent_data.get("local_path")
            
            analysis.update({
                "requires_mcp_action": True,
                "recommended_mcp_tool": "photo_vibe_check",
                "recommended_tool_name": "add_pre_event_photos",
                "recommended_action": "add_pre_event_photos",
                "confidence": 0.9,
                "reasoning": f"Promotion image upload requires MCP photo_vibe_check tool to add as pre-event reference photo",
                "mcp_tool_args": {
                    "event_id": event_id,
                    "admin_user_id": cloudevent_data.get("user_id"),
                    "photo_urls": [local_path] if local_path else [],
                    "guild_id": cloudevent_data.get("guild_id")
                }
            })
        
        return analysis