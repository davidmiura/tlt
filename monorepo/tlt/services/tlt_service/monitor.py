"""Monitoring endpoints for TLT Service"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from loguru import logger

router = APIRouter()

class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str
    status: str
    task_type: str
    priority: str
    created_at: str
    updated_at: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ServiceStatusResponse(BaseModel):
    """Response model for service status"""
    running: bool
    debug_mode: bool
    queue_size: int
    pending_tasks: int
    completed_tasks: int
    uptime_seconds: Optional[float]
    metrics: Dict[str, Any]
    agent_metrics: Dict[str, Any]

class TaskListResponse(BaseModel):
    """Response model for task list"""
    tasks: List[Dict[str, Any]]
    total_count: int
    filtered_count: int

@router.get("/status", response_model=ServiceStatusResponse)
async def get_service_status():
    """Get overall service status"""
    try:
        # Import here to avoid circular imports
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        status = await agent_manager.get_status()
        return ServiceStatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Error getting service status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        task_status = await agent_manager.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        return TaskStatusResponse(**task_status)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by task status"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of tasks to return")
):
    """List tasks with optional filtering"""
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        tasks = await agent_manager.list_tasks(status=status, limit=limit)
        
        return TaskListResponse(
            tasks=tasks,
            total_count=len(tasks),
            filtered_count=len(tasks)
        )
        
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Detailed health check for monitoring"""
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        health_status = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "tlt_service",
            "status": "healthy"
        }
        
        if agent_manager:
            agent_status = await agent_manager.get_status()
            health_status.update({
                "agent_running": agent_status["running"],
                "queue_size": agent_status["queue_size"],
                "pending_tasks": agent_status["pending_tasks"],
                "uptime_seconds": agent_status["uptime_seconds"]
            })
            
            # Check if agent is healthy
            if not agent_status["running"]:
                health_status["status"] = "degraded"
            elif agent_status["queue_size"] > 100:
                health_status["status"] = "warning"
                health_status["warning"] = "High queue size"
        else:
            health_status["status"] = "unhealthy"
            health_status["error"] = "Agent manager not initialized"
        
        status_code = 200
        if health_status["status"] == "unhealthy":
            status_code = 503
        elif health_status["status"] == "degraded":
            status_code = 503
        elif health_status["status"] == "warning":
            status_code = 200  # Still healthy, just warning
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "tlt_service",
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/metrics")
async def get_metrics():
    """Get detailed metrics for monitoring"""
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        status = await agent_manager.get_status()
        
        # Calculate additional metrics
        total_tasks = status["metrics"]["tasks_completed"] + status["metrics"]["tasks_failed"]
        success_rate = 0
        if total_tasks > 0:
            success_rate = status["metrics"]["tasks_completed"] / total_tasks * 100
        
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service_metrics": {
                "uptime_seconds": status["uptime_seconds"],
                "tasks_received": status["metrics"]["tasks_received"],
                "tasks_completed": status["metrics"]["tasks_completed"],
                "tasks_failed": status["metrics"]["tasks_failed"],
                "tasks_pending": status["pending_tasks"],
                "success_rate_percent": round(success_rate, 2),
                "rate_limit_hits": status["metrics"]["rate_limit_hits"],
                "queue_size": status["queue_size"]
            },
            "agent_metrics": status["agent_metrics"]
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/clear-completed-tasks")
async def clear_completed_tasks():
    """Clear completed tasks to free up memory"""
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        # Clear completed tasks
        cleared_count = len(agent_manager.completed_tasks)
        agent_manager.completed_tasks.clear()
        
        logger.info(f"Cleared {cleared_count} completed tasks")
        
        return {
            "message": f"Cleared {cleared_count} completed tasks",
            "cleared_count": cleared_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing completed tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug/agent-state")
async def get_agent_state():
    """Get current agent state (debug endpoint)"""
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        # Return agent manager state instead of agent state
        return {
            "agent_manager_state": {
                "agent_id": getattr(agent_manager, 'agent_id', None),
                "debug_mode": agent_manager.debug_mode,
                "running": agent_manager.running,
                "pending_tasks_count": len(agent_manager.pending_tasks),
                "completed_tasks_count": len(agent_manager.completed_tasks),
                "mode": "event_driven"
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/state")
async def get_agent_state_for_discord():
    """Get agent state for Discord adapter periodic queries"""
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        # Get the actual agent state if available
        agent_state = None
        if agent_manager.agent and hasattr(agent_manager.agent, 'current_state'):
            agent_state = agent_manager.agent.current_state
        
        # Prepare response with guild-specific state
        response = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_running": agent_manager.running,
            "agent_state_available": agent_state is not None,
            "agent_state_by_guild": {}
        }
        
        if agent_state:
            # Extract guild-specific information
            registered_guilds = agent_state.get("registered_guilds", {})
            rsvp_predictions = agent_state.get("rsvp_predictions", {})
            
            # Group state by guild
            for guild_id, guild_info in registered_guilds.items():
                guild_state = {
                    "guild_info": guild_info,
                    "pending_messages": [],
                    "event_updates": [],
                    "user_notifications": [],
                    "rsvp_predictions": {}
                }
                
                # Add RSVP predictions for this guild
                for prediction_key, prediction_data in rsvp_predictions.items():
                    if prediction_key.startswith(f"{guild_id}_"):
                        guild_state["rsvp_predictions"][prediction_key] = prediction_data
                
                # Add any pending messages for this guild
                pending_messages = agent_state.get("pending_messages", [])
                for message in pending_messages:
                    if message.get("guild_id") == guild_id:
                        guild_state["pending_messages"].append({
                            "channel_id": message.get("channel_id"),
                            "content": message.get("content"),
                            "priority": message.get("priority", "normal")
                        })
                
                response["agent_state_by_guild"][guild_id] = guild_state
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent state for Discord: {e}")
        raise HTTPException(status_code=500, detail=str(e))