"""Event management endpoints for TLT Service - Cleaned up version"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from loguru import logger

router = APIRouter()

# Response Models
class TaskResponse(BaseModel):
    """Response model for task submission"""
    task_id: str
    message: str
    status: str
    submitted_at: str

@router.post("/batch/submit")
async def submit_batch_tasks(
    tasks: list[Dict[str, Any]] = Body(..., description="List of tasks to submit")
):
    """
    Submit multiple tasks in batch.
    
    This endpoint allows submitting multiple tasks at once for batch processing.
    Each task should have: task_type, data, and optional priority.
    
    Args:
        tasks: List of task dictionaries with task_type, data, and priority
        
    Returns:
        dict: Summary of submitted and failed tasks
        
    Raises:
        HTTPException: If agent manager unavailable or batch size exceeded
    """
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        if len(tasks) > 50:
            raise HTTPException(status_code=400, detail="Batch size limited to 50 tasks")
        
        submitted_tasks = []
        failed_tasks = []
        
        for i, task_data in enumerate(tasks):
            try:
                task_type = task_data.get("task_type")
                data = task_data.get("data", {})
                priority = task_data.get("priority", "normal")
                
                if not task_type:
                    failed_tasks.append({
                        "index": i,
                        "error": "Missing task_type"
                    })
                    continue
                
                task_id = await agent_manager.submit_task(
                    task_type=task_type,
                    data=data,
                    priority=priority
                )
                
                submitted_tasks.append({
                    "index": i,
                    "task_id": task_id,
                    "task_type": task_type
                })
                
            except Exception as e:
                failed_tasks.append({
                    "index": i,
                    "error": str(e)
                })
        
        logger.info(f"Batch submitted: {len(submitted_tasks)} successful, {len(failed_tasks)} failed")
        
        return {
            "submitted_tasks": submitted_tasks,
            "failed_tasks": failed_tasks,
            "total_submitted": len(submitted_tasks),
            "total_failed": len(failed_tasks),
            "submitted_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch submit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}/result")
async def get_task_result(task_id: str):
    """
    Get the result of a completed task.
    
    This endpoint allows checking the status and result of any task
    submitted through the ambient agent system.
    
    Args:
        task_id: The unique task identifier
        
    Returns:
        dict: Task status, result, or error information
        
    Raises:
        HTTPException: If agent manager unavailable or task not found
    """
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        task_status = await agent_manager.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        
        if task_status["status"] == "pending":
            return {
                "task_id": task_id,
                "status": "pending",
                "message": "Task is still being processed"
            }
        elif task_status["status"] == "processing":
            return {
                "task_id": task_id,
                "status": "processing",
                "message": "Task is currently being processed"
            }
        elif task_status["status"] == "completed":
            return {
                "task_id": task_id,
                "status": "completed",
                "result": task_status["result"],
                "completed_at": task_status["updated_at"]
            }
        elif task_status["status"] == "failed":
            return {
                "task_id": task_id,
                "status": "failed",
                "error": task_status["error"],
                "failed_at": task_status["updated_at"]
            }
        else:
            return {
                "task_id": task_id,
                "status": task_status["status"],
                "message": "Unknown status"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task result for {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a pending task.
    
    This endpoint allows cancelling tasks that are still pending
    in the agent's task queue.
    
    Args:
        task_id: The unique task identifier
        
    Returns:
        dict: Cancellation confirmation and timestamp
        
    Raises:
        HTTPException: If agent manager unavailable, task not found, or task cannot be cancelled
    """
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        if not agent_manager:
            raise HTTPException(status_code=503, detail="Agent manager not initialized")
        
        # Check if task exists and is pending
        if task_id not in agent_manager.pending_tasks:
            # Check if it's completed
            if task_id in agent_manager.completed_tasks:
                raise HTTPException(status_code=409, detail="Task already completed, cannot cancel")
            else:
                raise HTTPException(status_code=404, detail="Task not found")
        
        task = agent_manager.pending_tasks[task_id]
        
        if task.status.value != "pending":
            raise HTTPException(status_code=409, detail=f"Task is {task.status.value}, cannot cancel")
        
        # Move to completed with cancelled status
        task.status = "failed"  # Using failed status for cancelled
        task.error = "Task cancelled by user"
        task.updated_at = datetime.now(timezone.utc)
        
        # Move from pending to completed
        del agent_manager.pending_tasks[task_id]
        agent_manager.completed_tasks[task_id] = task
        
        logger.info(f"Task {task_id} cancelled by user")
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancelled successfully",
            "cancelled_at": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def event_manager_health():
    """
    Health check for event manager functionality.
    
    Returns:
        dict: Health status and available endpoints
    """
    try:
        from tlt.services.tlt_service.main import agent_manager
        
        agent_available = agent_manager is not None
        
        return {
            "status": "healthy",
            "agent_available": agent_available,
            "endpoints": [
                "POST /events/batch/submit - Submit multiple tasks in batch",
                "GET /events/task/{task_id}/result - Get task result",
                "DELETE /events/task/{task_id} - Cancel pending task"
            ],
            "note": "Discord adapter now uses /cloudevents endpoint for event processing"
        }
        
    except Exception as e:
        logger.error(f"Error in event manager health check: {e}")
        return {
            "status": "error",
            "error": str(e)
        }