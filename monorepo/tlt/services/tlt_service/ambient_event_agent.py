"""Ambient Event Agent Manager for TLT Service"""

import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from loguru import logger

# Import the actual agent
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tlt.agents.ambient_event_agent.agent.agent import AmbientEventAgent
from tlt.shared.models.agent_task import AgentTask, TaskStatus

class AmbientEventAgentManager:
    """Manager for the ambient event agent with queue and rate limiting"""
    
    def __init__(self, openai_api_key: str, debug_mode: bool = False):
        self.openai_api_key = openai_api_key
        self.debug_mode = debug_mode
        self.agent: Optional[AmbientEventAgent] = None
        
        # Task management
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.pending_tasks: Dict[str, AgentTask] = {}
        self.completed_tasks: Dict[str, AgentTask] = {}
        self.max_completed_tasks = 1000  # Keep last 1000 completed tasks
        
        # Rate limiting
        self.rate_limit_requests_per_minute = 30
        self.rate_limit_window = []  # List of timestamps
        
        # Worker management
        self.worker_task: Optional[asyncio.Task] = None
        self.agent_task: Optional[asyncio.Task] = None
        self.running = False
        
        # Metrics
        self.metrics = {
            "tasks_received": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "rate_limit_hits": 0,
            "uptime_start": None
        }
        
        logger.debug("AmbientEventAgentManager initialized")
    
    async def start(self):
        """Start the agent manager"""
        try:
            logger.debug("Starting AmbientEventAgentManager")
            
            # Create agent configuration
            config = {
                "recursion_limit": 1000,  # Much higher limit for proper event processing
                "max_retry_attempts": 3,
                "enable_loop_detection": True,
                "max_iterations": None  # No iteration limit for continuous mode
            }
            
            # Create a minimal agent configuration for event-driven processing
            agent_id = f"tlt_service_agent_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            
            # Initialize the LangGraph agent
            try:
                self.agent = AmbientEventAgent(
                    openai_api_key=self.openai_api_key,
                    agent_id=agent_id,
                    debug_mode=self.debug_mode,
                    config=config
                )
                
                # Actually initialize the agent
                logger.debug(f"Initializing LangGraph agent {agent_id}...")
                await self.agent.initialize()
                logger.debug(f"LangGraph agent {agent_id} initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize LangGraph agent: {e}")
                # Continue without agent for basic functionality
                self.agent = None
            
            self.agent_id = agent_id
            self.agent_config = config
            
            # Start background tasks
            self.running = True
            self.metrics["uptime_start"] = datetime.now(timezone.utc)
            
            # Start worker task for processing submitted tasks
            self.worker_task = asyncio.create_task(self._worker_loop())
            
            # Start the agent's continuous background loop
            if self.agent:
                logger.debug("Starting ambient agent continuous loop...")
                self.agent_task = asyncio.create_task(self._agent_loop())
            
            logger.debug(f"Agent manager {agent_id} initialized successfully (continuous mode)")
            
            logger.debug("AmbientEventAgentManager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start AmbientEventAgentManager: {e}")
            raise
    
    async def stop(self):
        """Stop the agent manager"""
        logger.debug("Stopping AmbientEventAgentManager")
        self.running = False
        
        # Cancel background tasks
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
        
        if self.agent_task:
            self.agent_task.cancel()
            try:
                await self.agent_task
            except asyncio.CancelledError:
                pass
        
        # Agent cleanup (if needed)
        logger.debug("Agent manager cleanup completed")
        
        logger.info("AmbientEventAgentManager stopped")
    
    async def submit_task(self, task_type: str, data: Dict[str, Any], priority: str = "normal") -> str:
        """Submit a task to the agent"""
        logger.info(f"Submitting task: {task_type} with data: {data}")
        # Rate limiting check
        if not self._check_rate_limit():
            self.metrics["rate_limit_hits"] += 1
            raise Exception("Rate limit exceeded. Please try again later.")
        
        # Create task
        task_id = str(uuid.uuid4())
        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            data=data,
            priority=priority
        )
        
        # Add to pending tasks
        self.pending_tasks[task_id] = task
        
        # Add to queue
        await self.task_queue.put(task)
        
        self.metrics["tasks_received"] += 1
        logger.info(f"Task {task_id} ({task_type}) submitted to queue")
        
        return task_id
    
    async def add_task(self, task: AgentTask) -> str:
        """
        Add an AgentTask directly to the agent (used by CloudEvents endpoint).
        This method accepts a pre-constructed AgentTask instance.
        
        Args:
            task: AgentTask instance to add to the queue
            
        Returns:
            str: The task ID
        """
        logger.info(f"Adding AgentTask: {task.task_id} ({task.task_type})")
        
        # Check rate limit
        if not self._check_rate_limit():
            self.metrics["rate_limit_hits"] += 1
            raise Exception("Rate limit exceeded. Please try again later.")
        
        # Add to pending tasks
        self.pending_tasks[task.task_id] = task
        
        # Add to queue
        await self.task_queue.put(task)
        
        self.metrics["tasks_received"] += 1
        logger.info(f"AgentTask {task.task_id} ({task.task_type}) added to queue")
        
        return task.task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task"""
        # Check pending tasks
        if task_id in self.pending_tasks:
            task = self.pending_tasks[task_id]
            return task.to_dict()
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return task.to_dict()
        
        return None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get manager status"""
        uptime = None
        if self.metrics["uptime_start"]:
            uptime = (datetime.now(timezone.utc) - self.metrics["uptime_start"]).total_seconds()
        
        return {
            "running": self.running,
            "debug_mode": self.debug_mode,
            "queue_size": self.task_queue.qsize(),
            "pending_tasks": len(self.pending_tasks),
            "completed_tasks": len(self.completed_tasks),
            "uptime_seconds": uptime,
            "metrics": self.metrics,
            "agent_id": getattr(self, 'agent_id', None),
            "agent_mode": "event_driven"
        }
    
    async def list_tasks(self, status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """List tasks with optional status filter"""
        tasks = []
        
        # Add pending tasks
        for task in self.pending_tasks.values():
            if status is None or task.status.value == status:
                tasks.append(task.to_dict())
        
        # Add completed tasks (most recent first)
        completed_list = sorted(
            self.completed_tasks.values(),
            key=lambda t: t.updated_at,
            reverse=True
        )
        
        for task in completed_list:
            if status is None or task.status.value == status:
                tasks.append(task.to_dict())
        
        # Sort by priority and creation time, then limit
        priority_order = {"urgent": 0, "high": 1, "normal": 2, "low": 3}
        tasks.sort(key=lambda t: (priority_order.get(t.get("priority", "normal"), 2), t["created_at"]))
        
        return tasks[:limit]
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limit"""
        now = datetime.now(timezone.utc)
        minute_ago = now.timestamp() - 60
        
        # Remove old timestamps
        self.rate_limit_window = [
            ts for ts in self.rate_limit_window if ts > minute_ago
        ]
        
        # Check if under limit
        if len(self.rate_limit_window) >= self.rate_limit_requests_per_minute:
            return False
        
        # Add current timestamp
        self.rate_limit_window.append(now.timestamp())
        return True
    
    async def _worker_loop(self):
        """Main worker loop to process tasks"""
        logger.info("Worker loop started")
        
        while self.running:
            try:
                # Get task from queue (with timeout)
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                # Process task
                await self._process_task(task)
                
            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(1)
        
        logger.info("Worker loop stopped")
    
    async def _process_task(self, task: AgentTask):
        """Process a single task"""
        try:
            logger.info(f"Processing task {task.task_id} ({task.task_type})")
            
            # Update task status using Pydantic model method
            task.mark_processing()
            
            # Process based on task type
            if task.task_type == "discord_message":
                result = await self._process_discord_message(task)
            elif task.task_type == "event_update":
                result = await self._process_event_update(task)
            elif task.task_type == "timer_trigger":
                result = await self._process_timer_trigger(task)
            elif task.task_type == "create_event":
                result = await self._process_create_event(task)
            elif task.task_type == "cloudevent":
                result = await self._process_cloudevent(task)
            elif task.task_type == "generic_task":
                result = await self._process_generic_task(task)
            else:
                raise ValueError(f"Unknown task type: {task.task_type}")
            
            # Mark as completed using Pydantic model method
            task.mark_completed(result)
            self.metrics["tasks_completed"] += 1
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            # Mark as failed using Pydantic model method
            task.mark_failed(str(e))
            self.metrics["tasks_failed"] += 1
        
        finally:
            # Move from pending to completed
            if task.task_id in self.pending_tasks:
                del self.pending_tasks[task.task_id]
            
            self.completed_tasks[task.task_id] = task
            
            # Cleanup old completed tasks
            if len(self.completed_tasks) > self.max_completed_tasks:
                oldest_tasks = sorted(
                    self.completed_tasks.items(),
                    key=lambda x: x[1].updated_at
                )
                for task_id, _ in oldest_tasks[:-self.max_completed_tasks]:
                    del self.completed_tasks[task_id]
    
    async def _process_discord_message(self, task: AgentTask) -> Dict[str, Any]:
        """Process a Discord message task"""
        logger.info(f"Processing Discord message task {task.task_id}")
        
        # Process the Discord message without using the continuous agent loop
        # For now, just log and simulate processing
        result = {
            "message": "Discord message processed successfully",
            "task_id": task.task_id,
            "guild_id": task.data.get("guild_id"),
            "channel_id": task.data.get("channel_id"),
            "user_id": task.data.get("user_id"),
            "content_length": len(task.data.get("content", "")),
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        return result
    
    async def _process_event_update(self, task: AgentTask) -> Dict[str, Any]:
        """Process an event update task"""
        logger.info(f"Processing event update task {task.task_id}")
        
        # Process the event update
        result = {
            "message": "Event update processed successfully",
            "task_id": task.task_id,
            "event_id": task.data.get("event_id"),
            "update_type": task.data.get("update_type"),
            "user_id": task.data.get("user_id"),
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        return result
    
    async def _process_timer_trigger(self, task: AgentTask) -> Dict[str, Any]:
        """Process a timer trigger task"""
        logger.info(f"Processing timer trigger task {task.task_id}")
        
        # Process the timer trigger
        event_id = task.data.get("event_id")
        timer_type = task.data.get("timer_type", "reminder")
        scheduled_time_str = task.data.get("scheduled_time", datetime.now(timezone.utc).isoformat())
        
        result = {
            "message": "Timer trigger processed successfully",
            "task_id": task.task_id,
            "event_id": event_id,
            "timer_type": timer_type,
            "scheduled_time": scheduled_time_str,
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        return result
    
    async def _process_create_event(self, task: AgentTask) -> Dict[str, Any]:
        """Process a create event task"""
        logger.info(f"Processing create event task {task.task_id}")
        
        # Extract event and interaction data
        event_data = task.data.get("event_data", {})
        interaction_data = task.data.get("interaction_data", {})
        message_id = task.data.get("message_id")
        
        # If we have a LangGraph agent, add the event to its state
        if self.agent:
            try:
                # Import required classes for state management
                from tlt.agents.ambient_event_agent.state.state import (
                    IncomingEvent, EventTriggerType, MessagePriority, 
                    DiscordContext, EventContext
                )
                
                # Create Discord context from interaction data
                discord_context = DiscordContext(
                    guild_id=interaction_data.get("guild_id"),
                    channel_id=interaction_data.get("channel_id"),
                    user_id=interaction_data.get("user_id"),
                    message_id=message_id
                )
                
                # Create event context from event data
                event_context = EventContext(
                    event_id=str(event_data.get("message_id", task.task_id)),
                    event_title=event_data.get("topic", "Unknown Event"),
                    event_description=f"Location: {event_data.get('location', 'TBD')}, Time: {event_data.get('time', 'TBD')}",
                    created_by=interaction_data.get("user_name", "Unknown"),
                    rsvp_count=0,
                    emoji_summary={}
                )
                
                # Create event dictionary for the LangGraph agent
                event_dict = {
                    "trigger_type": "create_event",
                    "priority": "normal",
                    "data": {
                        "event_data": event_data,
                        "interaction_data": interaction_data,
                        "task_id": task.task_id,
                        "discord_context": discord_context,
                        "event_context": event_context
                    },
                    "metadata": task.data.get("metadata", {})
                }
                
                # Get current state and add the event
                current_state = self.agent.current_state
                if current_state is None:
                    logger.warning("Agent state is None, creating initial state")
                    from tlt.agents.ambient_event_agent.state.state import create_initial_state
                    current_state = create_initial_state(self.agent.agent_id)
                    self.agent.current_state = current_state
                
                # Add to pending events using the agent's method (synchronous)
                self.agent.add_event(event_dict)
                logger.info(f"Added create event to agent state: {event_data.get('topic', 'Unknown')} by {interaction_data.get('user_name', 'Unknown')}")
                
                # The continuous agent loop will pick up this event automatically
                logger.debug("Event added to agent state - continuous loop will process it")
                
            except Exception as e:
                logger.error(f"Error adding event to LangGraph agent: {e}")
                # Continue with basic processing even if agent integration fails
        
        result = {
            "message": "Event creation processed successfully",
            "task_id": task.task_id,
            "event_data": event_data,
            "interaction_data": interaction_data,
            "message_id": message_id,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "status": "event_created",
            "added_to_agent": self.agent is not None
        }
        
        # Log the event creation details
        logger.info(f"Event created: {event_data.get('topic', 'Unknown')} by {interaction_data.get('user_name', 'Unknown')}")
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        return result
    
    async def _process_cloudevent(self, task: AgentTask) -> Dict[str, Any]:
        """Process a CloudEvent task - passes CloudEvent directly to ambient agent"""
        logger.info(f"Processing CloudEvent task {task.task_id}")
        # logger.info(f"Processing CloudEvent task raw {task.model_dump()}")
        
        # Extract CloudEvent from task data
        cloudevent = task.data.get("cloudevent")
        if not cloudevent:
            raise ValueError("CloudEvent data missing from task")
        
        event_type = cloudevent.get("type", "unknown")
        event_source = cloudevent.get("source", "unknown")
        event_id = cloudevent.get("id", task.task_id)
        
        logger.info(f"Processing CloudEvent: type={event_type}, source={event_source}, id={event_id}")
        
        # If we have a LangGraph agent, pass AgentTask directly to it
        if self.agent:
            try:
                # Get current state
                current_state = self.agent.current_state
                if current_state is None:
                    logger.warning("Agent state is None, creating initial state")
                    from tlt.agents.ambient_event_agent.state.state import create_initial_state
                    current_state = create_initial_state(self.agent.agent_id)
                    self.agent.current_state = current_state
                
                # Pass AgentTask directly to agent without transformation
                self.agent.add_event(task)
                logger.info(f"Added AgentTask directly to agent state: {task.task_id} ({event_type})")
                
                # Wait for the agent to actually process the AgentTask
                logger.debug("Waiting for ambient agent to process AgentTask...")
                await self._wait_for_agent_task_completion(task.task_id, timeout=30.0)
                logger.info(f"AgentTask {task.task_id} processing completed by ambient agent")
                
            except Exception as e:
                logger.error(f"Error processing CloudEvent through LangGraph agent: {e}")
                # Continue with basic processing even if agent integration fails
        
        result = {
            "message": "CloudEvent processed successfully",
            "task_id": task.task_id,
            "event_id": task.event_id,
            "trigger_type": task.trigger_type.value,
            "message_priority": task.message_priority.value,
            "cloudevent": {
                "type": event_type,
                "source": event_source,
                "id": event_id,
                "specversion": cloudevent.get("specversion", "1.0")
            },
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "status": "cloudevent_processed",
            "added_to_agent": self.agent is not None
        }
        
        # Log the CloudEvent processing details
        logger.info(f"CloudEvent processed: {event_type} from {event_source}")
    
    async def _wait_for_agent_task_completion(self, task_id: str, timeout: float = 500.0):
        """Wait for the ambient agent to complete processing an AgentTask"""
        import asyncio
        from tlt.agents.ambient_event_agent.state.state import AgentTaskLifecycleStatus
        
        start_time = asyncio.get_event_loop().time()
        check_interval = 0.1  # Check every 100ms
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            try:
                # Check if agent has current state
                if not self.agent or not self.agent.current_state:
                    await asyncio.sleep(check_interval)
                    continue
                
                # Check agent task lifecycles
                agent_task_lifecycles = self.agent.current_state.get("agent_task_lifecycles", {})
                if task_id in agent_task_lifecycles:
                    lifecycle = agent_task_lifecycles[task_id]
                    
                    # Check if task reached a final status
                    if lifecycle.final_status in [
                        AgentTaskLifecycleStatus.COMPLETED,
                        AgentTaskLifecycleStatus.ABANDONED, 
                        AgentTaskLifecycleStatus.ERROR
                    ]:
                        logger.info(f"AgentTask {task_id} completed with status: {lifecycle.final_status}")
                        
                        # Log the final provenance trace
                        from tlt.agents.ambient_event_agent.state.state import log_agent_task_provenance
                        log_agent_task_provenance(self.agent.current_state, task_id, lifecycle.final_status, logger)
                        
                        return
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error checking AgentTask completion: {e}")
                await asyncio.sleep(check_interval)
        
        # Timeout reached
        logger.warning(f"Timeout waiting for AgentTask {task_id} completion after {timeout}s")
        
        # Log current lifecycle state for debugging
        if self.agent and self.agent.current_state:
            agent_task_lifecycles = self.agent.current_state.get("agent_task_lifecycles", {})
            if task_id in agent_task_lifecycles:
                lifecycle = agent_task_lifecycles[task_id]
                logger.info(f"AgentTask {task_id} timeout - current status: {lifecycle.final_status}, entries: {len(lifecycle.entries)}")
                
                # Log partial provenance trace even on timeout
                from tlt.agents.ambient_event_agent.state.state import log_agent_task_provenance
                log_agent_task_provenance(self.agent.current_state, task_id, AgentTaskLifecycleStatus.ABANDONED, logger)
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
    
    async def _process_generic_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a generic task"""
        logger.info(f"Processing generic task {task.task_id}")
        
        result = {
            "message": "Generic task processed successfully",
            "task_id": task.task_id,
            "data_keys": list(task.data.keys()),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "status": "generic_task_processed"
        }
        
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        return result
    
    async def _agent_loop(self):
        """Background loop for agent continuous operation"""
        logger.info("Agent loop started")
        
        try:
            # Run agent continuously but with limited iterations for production
            await self.agent.run_continuous(max_iterations=None, sleep_interval=10.0)
        except Exception as e:
            logger.error(f"Agent loop error: {e}")
        
        logger.info("Agent loop stopped")