"""State definitions for the ambient event agent"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Literal
from typing_extensions import TypedDict, Annotated
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from enum import Enum

class EventTriggerType(str, Enum):
    """Types of event triggers"""
    DISCORD_MESSAGE = "discord_message"
    TIMER_TRIGGER = "timer_trigger"
    RSVP_REMINDER = "rsvp_reminder"
    EVENT_FOLLOWUP = "event_followup"
    MANUAL_TRIGGER = "manual_trigger"
    CREATE_EVENT = "create_event"
    CLOUDEVENT = "cloudevent"
    # CloudEvent specific types
    CLOUDEVENT_CREATE_EVENT = "cloudevent_create_event"
    CLOUDEVENT_REGISTER_GUILD = "cloudevent_register_guild"
    CLOUDEVENT_DEREGISTER_GUILD = "cloudevent_deregister_guild"
    CLOUDEVENT_UPDATE_EVENT = "cloudevent_update_event"
    CLOUDEVENT_DELETE_EVENT = "cloudevent_delete_event"
    CLOUDEVENT_LIST_EVENTS = "cloudevent_list_events"
    CLOUDEVENT_EVENT_INFO = "cloudevent_event_info"
    CLOUDEVENT_RSVP_EVENT = "cloudevent_rsvp_event"
    CLOUDEVENT_PHOTO_VIBE_CHECK = "cloudevent_photo_vibe_check"

class MessagePriority(str, Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class AgentStatus(str, Enum):
    """Agent operational status"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    STOPPING = "stopping"

class CloudEventContext(BaseModel):
    """CloudEvent-specific context"""
    cloudevent_id: str
    cloudevent_type: str
    cloudevent_source: str
    cloudevent_subject: Optional[str] = None
    cloudevent_time: Optional[datetime] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    
class EventContext(BaseModel):
    """Context information about an event"""
    event_id: str
    event_title: str
    event_description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    created_by: str
    rsvp_count: int = 0
    emoji_summary: Dict[str, int] = Field(default_factory=dict)

class DiscordContext(BaseModel):
    """Discord-specific context"""
    guild_id: Optional[str] = None
    channel_id: str
    user_id: str
    message_id: Optional[str] = None
    thread_id: Optional[str] = None
    
class TimerContext(BaseModel):
    """Timer-specific context"""
    timer_type: str  # "1_day_before", "day_of", "event_time", "followup"
    event_id: str
    scheduled_time: datetime
    
class IncomingEvent(BaseModel):
    """Represents an incoming event to be processed"""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: EventTriggerType
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Context data
    discord_context: Optional[DiscordContext] = None
    timer_context: Optional[TimerContext] = None
    event_context: Optional[EventContext] = None
    cloudevent_context: Optional[CloudEventContext] = None
    
    # Raw data
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ScheduledTimer(BaseModel):
    """Represents a scheduled timer"""
    timer_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    timer_type: str
    scheduled_time: datetime
    priority: MessagePriority = MessagePriority.NORMAL
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentDecision(BaseModel):
    """Represents a decision made by the agent"""
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_type: str  # "send_message", "schedule_timer", "no_action", etc.
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class MessageToSend(BaseModel):
    """Represents a message to be sent"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    channel_id: str
    content: str
    priority: MessagePriority = MessagePriority.NORMAL
    scheduled_time: Optional[datetime] = None  # If None, send immediately
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentTaskLifecycleStatus(str, Enum):
    """Lifecycle status for AgentTask processing"""
    RECEIVED = "received"           # AgentTask received by agent
    QUEUED = "queued"              # Added to pending_events
    PROCESSING = "processing"       # Being processed by a node
    EVENT_MONITOR = "event_monitor" # In event monitor node
    REASONING = "reasoning"         # In reasoning node  
    MCP_EXECUTOR = "mcp_executor"   # In MCP executor node
    DISCORD_INTERFACE = "discord_interface"  # In Discord interface node
    COMPLETED = "completed"         # Successfully completed
    ABANDONED = "abandoned"         # Abandoned due to error or timeout
    ERROR = "error"                 # Failed with error

class AgentTaskLifecycleEntry(BaseModel):
    """Single lifecycle entry for an AgentTask"""
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: AgentTaskLifecycleStatus
    node_name: Optional[str] = None
    details: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentTaskLifecycle(BaseModel):
    """Complete lifecycle tracking for an AgentTask"""
    task_id: str
    event_id: str
    agent_task_type: str = ""       # Original AgentTask trigger type
    cloudevent_type: Optional[str] = None  # CloudEvent type if applicable
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    final_status: Optional[AgentTaskLifecycleStatus] = None
    entries: List[AgentTaskLifecycleEntry] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)  # Trace data

class AgentState(TypedDict):
    """Main state for the ambient event agent"""
    
    # Agent status and control
    status: AgentStatus
    agent_id: str
    started_at: datetime
    last_activity: datetime
    iteration_count: int
    monitoring_cycles: int  # Track event monitoring cycles for loop detection
    
    # Current processing context
    current_event: Optional[IncomingEvent]
    processing_step: str
    
    # Message history and conversation context
    messages: Annotated[List[BaseMessage], add_messages]
    conversation_history: List[Dict[str, Any]]
    
    # Event and timer management
    active_timers: List[ScheduledTimer]
    pending_events: List[IncomingEvent] = Field(default_factory=list)
    processed_events: List[str]  # Event IDs that have been processed
    
    # Decision tracking
    recent_decisions: List[AgentDecision]
    pending_messages: List[MessageToSend]
    pending_mcp_requests: List[Dict[str, Any]]
    
    # Context caches
    event_cache: Dict[str, EventContext]  # event_id -> EventContext
    user_context: Dict[str, Dict[str, Any]]  # user_id -> context
    
    # Configuration and settings
    config: Dict[str, Any]
    debug_mode: bool
    
    # Error handling
    error_history: List[Dict[str, Any]]
    retry_count: int
    
    # MCP tool availability
    available_tools: List[str]
    tool_call_history: List[Dict[str, Any]]
    
    # AgentTask lifecycle tracking
    agent_task_lifecycles: Dict[str, AgentTaskLifecycle]  # task_id -> lifecycle
    current_processing_tasks: List[str]  # task_ids currently being processed

def create_initial_state(agent_id: str = None) -> AgentState:
    """Create initial agent state"""
    if agent_id is None:
        agent_id = str(uuid.uuid4())
    
    now = datetime.now(timezone.utc)
    
    return AgentState(
        # Agent status and control
        status=AgentStatus.INITIALIZING,
        agent_id=agent_id,
        started_at=now,
        last_activity=now,
        iteration_count=0,
        monitoring_cycles=0,
        
        # Current processing context
        current_event=None,
        processing_step="initializing",
        
        # Message history and conversation context
        messages=[],
        conversation_history=[],
        
        # Event and timer management
        active_timers=[],
        pending_events=[],
        processed_events=[],
        
        # Decision tracking
        recent_decisions=[],
        pending_messages=[],
        pending_mcp_requests=[],
        
        # Context caches
        event_cache={},
        user_context={},
        
        # Configuration and settings
        config={
            "max_pending_events": 100,
            "max_conversation_history": 1000,
            "timer_check_interval": 60,  # seconds
            "max_retry_attempts": 3,
            "message_rate_limit": 10,  # messages per minute
        },
        debug_mode=False,
        
        # Error handling
        error_history=[],
        retry_count=0,
        
        # MCP tool availability
        available_tools=[],
        tool_call_history=[],
        
        # AgentTask lifecycle tracking
        agent_task_lifecycles={},
        current_processing_tasks=[],
        
        # Guild and RSVP state management
        registered_guilds={},
        rsvp_predictions={},
        agent_state_by_guild={}
    )

def track_agent_task_lifecycle(
    state: AgentState, 
    task_id: str, 
    event_id: str,
    status: AgentTaskLifecycleStatus,
    node_name: Optional[str] = None,
    details: str = "",
    agent_task_type: str = "",
    cloudevent_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Track AgentTask lifecycle status and log verbose details"""
    
    # Get or create lifecycle tracker
    if task_id not in state["agent_task_lifecycles"]:
        state["agent_task_lifecycles"][task_id] = AgentTaskLifecycle(
            task_id=task_id,
            event_id=event_id,
            agent_task_type=agent_task_type,
            cloudevent_type=cloudevent_type
        )
    
    lifecycle = state["agent_task_lifecycles"][task_id]
    
    # Add lifecycle entry
    entry = AgentTaskLifecycleEntry(
        status=status,
        node_name=node_name,
        details=details,
        metadata=metadata or {}
    )
    lifecycle.entries.append(entry)
    
    # Update current processing tasks list
    if status in [AgentTaskLifecycleStatus.PROCESSING, AgentTaskLifecycleStatus.EVENT_MONITOR, 
                  AgentTaskLifecycleStatus.REASONING, AgentTaskLifecycleStatus.MCP_EXECUTOR,
                  AgentTaskLifecycleStatus.DISCORD_INTERFACE]:
        if task_id not in state["current_processing_tasks"]:
            state["current_processing_tasks"].append(task_id)
    elif status in [AgentTaskLifecycleStatus.COMPLETED, AgentTaskLifecycleStatus.ABANDONED, 
                    AgentTaskLifecycleStatus.ERROR]:
        if task_id in state["current_processing_tasks"]:
            state["current_processing_tasks"].remove(task_id)
        lifecycle.completed_at = datetime.now(timezone.utc)
        lifecycle.final_status = status

def get_agent_task_provenance(state: AgentState, task_id: str) -> Dict[str, Any]:
    """Get complete provenance trace for an AgentTask"""
    if task_id not in state["agent_task_lifecycles"]:
        return {}
    
    lifecycle = state["agent_task_lifecycles"][task_id]
    
    # Build provenance trace
    trace = {
        "task_id": task_id,
        "event_id": lifecycle.event_id,
        "agent_task_type": lifecycle.agent_task_type,
        "cloudevent_type": lifecycle.cloudevent_type,
        "created_at": lifecycle.created_at.isoformat(),
        "completed_at": lifecycle.completed_at.isoformat() if lifecycle.completed_at else None,
        "final_status": lifecycle.final_status.value if lifecycle.final_status else None,
        "total_duration_seconds": (
            (lifecycle.completed_at - lifecycle.created_at).total_seconds()
            if lifecycle.completed_at else None
        ),
        "lifecycle_entries": [
            {
                "timestamp": entry.timestamp.isoformat(),
                "status": entry.status.value,
                "node_name": entry.node_name,
                "details": entry.details,
                "metadata": entry.metadata
            }
            for entry in lifecycle.entries
        ],
        "nodes_visited": list(set([
            entry.node_name for entry in lifecycle.entries 
            if entry.node_name
        ])),
        "status_history": [entry.status.value for entry in lifecycle.entries]
    }
    
    return trace

def log_agent_task_provenance(state: AgentState, task_id: str, final_status: AgentTaskLifecycleStatus, logger) -> None:
    """Log complete provenance trace for an AgentTask at INFO level"""
    
    # Mark task as completed/abandoned
    lifecycle = state.get("agent_task_lifecycles", {}).get(task_id)
    event_id = lifecycle.event_id if lifecycle else "unknown"
    
    track_agent_task_lifecycle(
        state,
        task_id=task_id,
        event_id=event_id,
        status=final_status,
        details=f"AgentTask lifecycle completed with status: {final_status.value}"
    )
    
    # Get complete provenance trace
    trace = get_agent_task_provenance(state, task_id)
    
    if not trace:
        logger.info(f"PROVENANCE: No trace found for AgentTask {task_id}")
        return
    
    # Log provenance trace as INFO
    logger.info(f"PROVENANCE TRACE for AgentTask {task_id}:")
    logger.info(f"  Task ID: {trace['task_id']}")
    logger.info(f"  Event ID: {trace['event_id']}")
    logger.info(f"  Agent Task Type: {trace['agent_task_type']}")
    logger.info(f"  CloudEvent Type: {trace['cloudevent_type']}")
    logger.info(f"  Created At: {trace['created_at']}")
    logger.info(f"  Completed At: {trace['completed_at']}")
    logger.info(f"  Final Status: {trace['final_status']}")
    logger.info(f"  Total Duration: {trace['total_duration_seconds']} seconds")
    logger.info(f"  Nodes Visited: {trace['nodes_visited']}")
    logger.info(f"  Status History: {' -> '.join(trace['status_history'])}")
    
    # Log each lifecycle entry
    logger.info(f"  Lifecycle Entries ({len(trace['lifecycle_entries'])} total):")
    for i, entry in enumerate(trace['lifecycle_entries']):
        logger.info(f"    {i+1}. [{entry['timestamp']}] {entry['status']} @ {entry['node_name']} - {entry['details']}")
        if entry['metadata']:
            logger.info(f"       Metadata: {entry['metadata']}")
    
    logger.info(f"PROVENANCE TRACE END for AgentTask {task_id}")

def check_and_log_abandoned_tasks(state: AgentState, logger, max_age_minutes: int = 30) -> None:
    """Check for and log abandoned AgentTasks that have been processing too long"""
    
    current_time = datetime.now(timezone.utc)
    abandoned_tasks = []
    
    for task_id, lifecycle in state.get("agent_task_lifecycles", {}).items():
        # Skip already completed tasks
        if lifecycle.final_status in [AgentTaskLifecycleStatus.COMPLETED, 
                                     AgentTaskLifecycleStatus.ABANDONED, 
                                     AgentTaskLifecycleStatus.ERROR]:
            continue
        
        # Check if task is too old
        age_minutes = (current_time - lifecycle.created_at).total_seconds() / 60
        if age_minutes > max_age_minutes:
            abandoned_tasks.append(task_id)
            
            # Log as abandoned
            log_agent_task_provenance(state, task_id, AgentTaskLifecycleStatus.ABANDONED, logger)
            logger.info(f"AgentTask {task_id} marked as ABANDONED after {age_minutes:.15f} minutes")
    
    return abandoned_tasks