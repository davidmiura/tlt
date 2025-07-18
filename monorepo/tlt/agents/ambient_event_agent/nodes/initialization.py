"""Initialization node for ambient event agent"""

import asyncio
from datetime import datetime, timezone
from typing import List

from tlt.agents.ambient_event_agent.nodes.base import BaseNode
from tlt.agents.ambient_event_agent.state.state import AgentState, AgentStatus

class InitializationNode(BaseNode):
    """Handle agent initialization and setup"""
    
    def __init__(self):
        super().__init__("initialization")
    
    async def execute(self, state: AgentState) -> AgentState:
        """Initialize the agent and its dependencies"""
        self.log_execution(state, "Starting agent initialization", level="debug")
        
        try:
            # Update status
            self.update_state_metadata(state, {
                "status": AgentStatus.INITIALIZING,
                "processing_step": "initializing"
            })
            
            # Initialize MCP connections
            await self._initialize_mcp_connections(state)
            
            # Load configuration
            await self._load_configuration(state)
            
            # Initialize timer system
            await self._initialize_timers(state)
            
            # Set up event monitoring
            await self._setup_event_monitoring(state)
            
            # Mark as ready
            self.update_state_metadata(state, {
                "status": AgentStatus.IDLE,
                "processing_step": "ready"
            })
            
            self.add_system_message(state, "Agent initialization completed successfully")
            self.log_execution(state, "Agent initialization completed", level="debug")
            
        except Exception as e:
            self.handle_error(state, e, "initialization")
            state["status"] = AgentStatus.ERROR
        
        return state
    
    async def _initialize_mcp_connections(self, state: AgentState):
        """Initialize connections to MCP services"""
        self.log_execution(state, "Initializing MCP connections", level="debug")
        
        # List of available MCP services
        expected_tools = [
            # Event Manager tools
            "create_event", "get_event", "update_event", "delete_event",
            "list_all_events", "get_events_by_creator", "get_events_by_status",
            "create_rsvp", "update_rsvp", "get_event_rsvps",
            
            # Photo Vibe Check tools (if available)
            "submit_photo_dm", "activate_photo_collection", "get_photo_status",
            
            # Vibe Bit tools (if available) 
            "create_canvas", "place_element", "view_canvas_progress"
        ]
        
        # For now, assume all tools are available
        # In production, this would probe actual MCP services
        state["available_tools"] = expected_tools
        
        self.log_execution(state, f"Initialized {len(expected_tools)} MCP tools", level="debug")
    
    async def _load_configuration(self, state: AgentState):
        """Load agent configuration"""
        self.log_execution(state, "Loading configuration", level="debug")
        
        # Default configuration
        config_updates = {
            "gateway_url": "http://localhost:8003",
            "event_manager_url": "http://localhost:8004",
            "photo_vibe_check_url": "http://localhost:8005", 
            "vibe_bit_url": "http://localhost:8006",
            "discord_rate_limit": 10,  # messages per minute
            "timer_precision": 60,  # check timers every 60 seconds
            "max_conversation_length": 1000,
            "reminder_schedule": {
                "1_day_before": 24 * 60,  # minutes before event
                "day_of": 8 * 60,  # 8 hours before event
                "event_time": 0,  # at event time
                "followup": -24 * 60  # 24 hours after event
            }
        }
        
        state["config"].update(config_updates)
        self.log_execution(state, "Configuration loaded", level="debug")
    
    async def _initialize_timers(self, state: AgentState, level="debug"):
        """Initialize the timer system"""
        self.log_execution(state, "Initializing timer system", level="debug")
        
        # Load any existing timers from persistence (if implemented)
        # For now, start with empty timer list
        state["active_timers"] = []
        
        self.log_execution(state, "Timer system initialized", level="debug")
    
    async def _setup_event_monitoring(self, state: AgentState, level="debug"):
        """Set up monitoring for incoming events"""
        self.log_execution(state, "Setting up event monitoring", level="debug")
        
        # Initialize event queues
        # state["pending_events"] = []
        
        # Set up monitoring contexts
        # This would connect to Discord adapter, etc.
        
        self.log_execution(state, "Event monitoring setup complete", level="debug")