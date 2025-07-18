"""CloudEvents router for TLT Service"""

import uuid
from fastapi import APIRouter, HTTPException
from loguru import logger
from typing import Optional

from tlt.shared.cloudevents import CloudEvent
from tlt.shared.models.agent_task import AgentTask, EventTriggerType, MessagePriority


# Create router for CloudEvents endpoints
router = APIRouter()

# Global agent manager reference (will be set by main.py)
_agent_manager: Optional[object] = None


def set_agent_manager(agent_manager):
    """Set the agent manager instance for the router"""
    global _agent_manager
    _agent_manager = agent_manager


def get_agent_manager():
    """Get the current agent manager instance"""
    return _agent_manager


@router.post("/cloudevents")
async def handle_cloudevent(cloudevent: CloudEvent):
    """
    Handle incoming CloudEvents and pass them directly to the ambient event agent.
    This endpoint does not transform the CloudEvent payload - it passes it as-is
    to the ambient_event_agent for processing.
    
    Args:
        cloudevent: The CloudEvent to process
        
    Returns:
        dict: Response with status and CloudEvent information
        
    Raises:
        HTTPException: If agent is unavailable or processing fails
    """
    logger.info(f"Received CloudEvent: type={cloudevent.type}, source={cloudevent.source}, id={cloudevent.id}")
    
    # Get the agent manager instance
    agent_manager = get_agent_manager()
    
    # Validate that we have an agent manager
    if not agent_manager:
        logger.error("Ambient event agent not available")
        raise HTTPException(
            status_code=503, 
            detail="Ambient event agent not available. Check service configuration."
        )
    
    try:
        # Create AgentTask directly from CloudEvent
        logger.info(f"Creating AgentTask from CloudEvent: {cloudevent.id}")
        
        # Determine task type from CloudEvent type
        task_type = "cloudevent"  # Generic CloudEvent handling
        
        # Construct task data payload
        task_data = {
            "cloudevent": cloudevent.model_dump(),
            "timestamp": cloudevent.time.isoformat() if cloudevent.time else None,
            "message_id": cloudevent.id,
            "event_type": cloudevent.type,
            "event_source": cloudevent.source
        }
        
        # Create AgentTask instance with enhanced fields
        agent_task = AgentTask(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            data=task_data,
            priority="normal",
            trigger_type=EventTriggerType.CLOUDEVENT,
            message_priority=MessagePriority.NORMAL,
            metadata={
                "cloudevent_type": cloudevent.type,
                "cloudevent_source": cloudevent.source,
                "cloudevent_id": cloudevent.id
            }
        )
        
        # Add AgentTask to agent manager's queue
        await agent_manager.add_task(agent_task)
        
        logger.info(f"CloudEvent {cloudevent.id} successfully queued as AgentTask {agent_task.task_id}")
        
        return {
            "status": "accepted",
            "cloudevent_id": cloudevent.id,
            "task_id": agent_task.task_id,
            "type": cloudevent.type,
            "source": cloudevent.source,
            "message": "CloudEvent queued for processing by ambient agent"
        }
        
    except Exception as e:
        logger.error(f"Failed to process CloudEvent {cloudevent.id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process CloudEvent: {str(e)}"
        )


@router.get("/cloudevents/health")
async def cloudevents_health():
    """
    Health check endpoint for CloudEvents functionality
    
    Returns:
        dict: Health status of CloudEvents processing
    """
    return {
        "status": "healthy",
        "endpoint": "/cloudevents",
        "capabilities": [
            "CloudEvents v1.0 compliant",
            "Direct ambient agent integration", 
            "No payload transformation",
            "Async task queuing"
        ],
        "supported_event_types": [
            "com.tlt.discord.create-event",
            "com.tlt.discord.update-event",
            "com.tlt.discord.delete-event",
            "com.tlt.discord.rsvp-event", 
            "com.tlt.discord.message",
            "com.tlt.discord.timer-trigger",
            "com.tlt.discord.manual-trigger",
            "com.tlt.discord.register-guild",
            "com.tlt.discord.deregister-guild",
            "com.tlt.discord.list-events",
            "com.tlt.discord.event-info",
            "com.tlt.discord.photo-vibe-check",
            "com.tlt.discord.vibe-action",
            "com.tlt.discord.promotion-image"
        ]
    }


@router.get("/cloudevents/stats")
async def cloudevents_stats():
    """
    Get CloudEvents processing statistics
    
    Returns:
        dict: Statistics about CloudEvents processing
        
    Raises:
        HTTPException: If agent manager is unavailable
    """
    # Get the agent manager instance
    agent_manager = get_agent_manager()
    
    if not agent_manager:
        raise HTTPException(
            status_code=503,
            detail="Agent manager not available"
        )
    
    try:
        agent_status = await agent_manager.get_status()
        
        return {
            "cloudevents_endpoint": "/cloudevents",
            "agent_running": agent_status.get("running", False),
            "queue_size": agent_status.get("queue_size", 0),
            "pending_tasks": agent_status.get("pending_tasks", 0),
            "completed_tasks": agent_status.get("completed_tasks", 0),
            "metrics": agent_status.get("metrics", {}),
            "agent_mode": agent_status.get("agent_mode", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Failed to get CloudEvents stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )