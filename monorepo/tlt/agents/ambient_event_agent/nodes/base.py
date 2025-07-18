"""Base node functionality for ambient event agent"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from loguru import logger

from tlt.agents.ambient_event_agent.state.state import AgentState, AgentStatus

class BaseNode(ABC):
    """Base class for all agent nodes"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    async def execute(self, state: AgentState) -> AgentState:
        """Execute the node logic"""
        pass
    
    def log_execution(self, state: AgentState, message: str, level: str = "info"):
        """Log node execution with context"""
        log_msg = f"[{self.name}] Step: {state['processing_step']} | {message}"
        
        if level == "debug":
            logger.debug(log_msg)
        elif level == "warning":
            logger.warning(log_msg)
        elif level == "error":
            logger.error(log_msg)
        else:
            logger.info(log_msg)
    
    def update_state_metadata(self, state: AgentState, updates: Dict[str, Any]):
        """Update state with metadata tracking"""
        state["last_activity"] = datetime.now(timezone.utc)
        state["iteration_count"] += 1
        
        # Add to conversation history if this is a significant step
        if "processing_step" in updates:
            state["conversation_history"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "node": self.name,
                "step": updates["processing_step"],
                "metadata": {k: v for k, v in updates.items() if k != "processing_step"}
            })
        
        # Apply updates
        for key, value in updates.items():
            if key in state:
                state[key] = value
    
    def add_system_message(self, state: AgentState, content: str):
        """Add a system message to the conversation"""
        msg = SystemMessage(content=f"[{self.name}] {content}")
        state["messages"].append(msg)
    
    def add_ai_message(self, state: AgentState, content: str):
        """Add an AI message to the conversation"""
        msg = AIMessage(content=content)
        state["messages"].append(msg)
    
    def add_human_message(self, state: AgentState, content: str):
        """Add a human message to the conversation"""
        msg = HumanMessage(content=content)
        state["messages"].append(msg)
    
    def handle_error(self, state: AgentState, error: Exception, context: str = ""):
        """Handle errors with consistent logging and state updates"""
        error_info = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "node": self.name,
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "processing_step": state.get("processing_step", "unknown")
        }
        
        state["error_history"].append(error_info)
        state["retry_count"] += 1
        
        self.log_execution(state, f"Error in {context}: {error}", "error")
        
        # Limit error history size
        if len(state["error_history"]) > 50:
            state["error_history"] = state["error_history"][-25:]
    
    def should_continue_processing(self, state: AgentState) -> bool:
        """Check if processing should continue based on state"""
        if state["status"] == AgentStatus.STOPPING:
            return False
            
        if state["retry_count"] > state["config"].get("max_retry_attempts", 3):
            self.log_execution(state, "Max retry attempts exceeded", "warning")
            return False
            
        return True