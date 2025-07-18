"""Event monitoring node for ambient event agent"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

from loguru import logger

from tlt.agents.ambient_event_agent.nodes.base import BaseNode
from tlt.agents.ambient_event_agent.state.state import (
    AgentState, AgentStatus, IncomingEvent, EventTriggerType, 
    MessagePriority, DiscordContext, TimerContext, EventContext, CloudEventContext,
    track_agent_task_lifecycle, AgentTaskLifecycleStatus, get_agent_task_provenance
)

class EventMonitorNode(BaseNode):
    """Monitor for incoming events from various sources"""
    
    def __init__(self):
        super().__init__("event_monitor")
    
    async def execute(self, state: AgentState) -> AgentState:
        """Monitor for new events and timers"""
        self.log_execution(state, "Checking for new events", level="debug")
        
        # Track all current processing tasks entering event monitor
        for task_id in state.get("current_processing_tasks", []):
            # Find the event_id for this task
            lifecycle = state.get("agent_task_lifecycles", {}).get(task_id)
            if lifecycle:
                track_agent_task_lifecycle(
                    state,
                    task_id=task_id,
                    event_id=lifecycle.event_id,
                    status=AgentTaskLifecycleStatus.EVENT_MONITOR,
                    node_name="event_monitor",
                    details="Entering event monitor node for processing"
                )
                logger.info(f"EventMonitor: Tracking AgentTask {task_id} in event monitor node")
        
        try:
            self.update_state_metadata(state, {
                "status": AgentStatus.PROCESSING,
                "processing_step": "monitoring_events"
            })
            
            # Increment monitoring cycles counter (moved from router)
            state["monitoring_cycles"] = state.get("monitoring_cycles", 0) + 1
            
            # Handle retry count increment if needed (moved from router)
            if state["status"] == AgentStatus.ERROR:
                state["retry_count"] = state.get("retry_count", 0) + 1
            
            # Check for timer-based events
            await self._check_timer_events(state)
            
            # Check for Discord events (simulated for now)
            await self._check_discord_events(state)
            
            # Check for manual/API events
            await self._check_manual_events(state)
            
            # Check and process CloudEvents in pending_events
            await self._process_cloudevents(state)
            
            # Update status based on what we found
            if state["pending_events"]:
                next_step = "event_available"
                self.log_execution(state, f"Found {len(state['pending_events'])} pending events")
            else:
                next_step = "no_events"
                state["status"] = AgentStatus.IDLE
            
            self.update_state_metadata(state, {
                "processing_step": next_step
            })
            
        except Exception as e:
            self.handle_error(state, e, "event monitoring")
            state["status"] = AgentStatus.ERROR
        
        return state
    
    async def _check_timer_events(self, state: AgentState):
        """Check for timer-based events that should trigger"""
        now = datetime.now(timezone.utc)
        triggered_timers = []
        
        for timer in state["active_timers"]:
            if timer.is_active and timer.scheduled_time <= now:
                self.log_execution(state, f"Timer triggered: {timer.timer_type} for event {timer.event_id}")
                
                # Create timer event
                timer_event = IncomingEvent(
                    trigger_type=EventTriggerType.TIMER_TRIGGER,
                    priority=timer.priority,
                    timer_context=TimerContext(
                        timer_type=timer.timer_type,
                        event_id=timer.event_id,
                        scheduled_time=timer.scheduled_time
                    ),
                    metadata={"timer_id": timer.timer_id}
                )
                
                state["pending_events"].append(timer_event)
                triggered_timers.append(timer)
                
                # Deactivate triggered timer
                timer.is_active = False
        
        if triggered_timers:
            self.log_execution(state, f"Triggered {len(triggered_timers)} timers")
    
    async def _check_discord_events(self, state: AgentState):
        """Check for Discord events"""
        # In a real implementation, this would:
        # 1. Connect to Discord adapter message queue
        # 2. Check for new messages, reactions, etc.
        # 3. Filter for relevant events
        
        # No simulation - events come from external sources via add_event()
        pass
    
    async def _check_manual_events(self, state: AgentState):
        """Check for manual/API triggered events"""
        # In a real implementation, this would check:
        # 1. API endpoints for manual triggers
        # 2. File system for trigger files
        # 3. Database for queued events
        
        # For now, this is a placeholder
        pass
    
    async def _get_event_context(self, event_id: str, state: AgentState) -> Optional[EventContext]:
        """Fetch event context from cache or MCP services"""
        # Check cache first
        if event_id in state["event_cache"]:
            return state["event_cache"][event_id]
        
        # In a real implementation, this would call MCP event manager
        # For now, return a mock context
        mock_context = EventContext(
            event_id=event_id,
            event_title="Mock Event",
            event_description="A simulated event for testing",
            start_time=datetime.now(timezone.utc) + timedelta(hours=2),
            created_by="system",
            rsvp_count=5,
            emoji_summary={"✅": 3, "❌": 1, "🤔": 1}
        )
        
        # Cache it
        state["event_cache"][event_id] = mock_context
        return mock_context
    
    async def _process_cloudevents(self, state: AgentState):
        """Process and classify CloudEvents in the pending events queue"""
        processed_events = []
        
        # Log CloudEvent processing start
        logger.debug(f"EventMonitor: Processing {len(state['pending_events'])} pending events for CloudEvent classification")
        
        for i, event in enumerate(state["pending_events"]):
            # Log each event being processed
            logger.info(f"EventMonitor: Processing event {i+1}/{len(state['pending_events'])}: event_id={event.event_id}, trigger_type={event.trigger_type}, raw_data={event.raw_data}")
            
            # Find associated AgentTask if this event came from one
            task_id = None
            agent_task_type = ""
            for tid, lifecycle in state.get("agent_task_lifecycles", {}).items():
                if lifecycle.event_id == event.event_id:
                    task_id = tid
                    agent_task_type = lifecycle.agent_task_type
                    break
            
            # Check if this event has CloudEvent data
            if self._is_cloudevent(event):
                logger.info(f"EventMonitor: Event {event.event_id} identified as CloudEvent")
                
                # Track AgentTask lifecycle if found
                if task_id:
                    track_agent_task_lifecycle(
                        state,
                        task_id=task_id,
                        event_id=event.event_id,
                        status=AgentTaskLifecycleStatus.PROCESSING,
                        node_name="event_monitor",
                        details="Processing CloudEvent classification and enhancement",
                        metadata={"is_cloudevent": True, "raw_trigger_type": event.trigger_type.value}
                    )
                
                # Classify and enhance the CloudEvent
                enhanced_event = await self._classify_cloudevent(event, state)
                if enhanced_event:
                    processed_events.append(enhanced_event)
                    self.log_execution(state, f"Processed CloudEvent: {enhanced_event.trigger_type}")
                    logger.info(f"EventMonitor: CloudEvent {event.event_id} enhanced to trigger_type={enhanced_event.trigger_type}")
                    
                    # Track enhancement success
                    if task_id:
                        track_agent_task_lifecycle(
                            state,
                            task_id=task_id,
                            event_id=event.event_id,
                            status=AgentTaskLifecycleStatus.PROCESSING,
                            node_name="event_monitor",
                            details=f"CloudEvent successfully enhanced to {enhanced_event.trigger_type}",
                            metadata={"enhanced_trigger_type": enhanced_event.trigger_type.value}
                        )
                else:
                    # Keep original event if classification failed
                    processed_events.append(event)
                    logger.info(f"EventMonitor: CloudEvent {event.event_id} classification failed, keeping original")
                    
                    # Track enhancement failure
                    if task_id:
                        track_agent_task_lifecycle(
                            state,
                            task_id=task_id,
                            event_id=event.event_id,
                            status=AgentTaskLifecycleStatus.PROCESSING,
                            node_name="event_monitor",
                            details="CloudEvent classification failed, using original event",
                            metadata={"enhancement_failed": True}
                        )
            else:
                # Keep non-CloudEvent events as-is
                processed_events.append(event)
                logger.info(f"EventMonitor: Event {event.event_id} is not a CloudEvent, keeping as-is")
                
                # Track non-CloudEvent processing
                if task_id:
                    track_agent_task_lifecycle(
                        state,
                        task_id=task_id,
                        event_id=event.event_id,
                        status=AgentTaskLifecycleStatus.PROCESSING,
                        node_name="event_monitor",
                        details="Event processed as non-CloudEvent",
                        metadata={"is_cloudevent": False}
                    )
        
        # Update pending events with processed events
        # TODO: Maybe the wrong pending_events logic
        state["pending_events"] = processed_events
    
    def _is_cloudevent(self, event: IncomingEvent) -> bool:
        """Check if an event is a CloudEvent"""
        # Check for CloudEvent indicators in raw_data or metadata
        cloudevent_data = event.raw_data.get("cloudevent") or event.metadata.get("cloudevent")
        if cloudevent_data:
            return True
        
        # Check trigger type
        if event.trigger_type == EventTriggerType.CLOUDEVENT:
            return True
        
        # Check for CloudEvent fields in raw_data
        if any(key in event.raw_data for key in ["type", "source", "id", "specversion"]):
            return True
            
        return False
    
    async def _classify_cloudevent(self, event: IncomingEvent, state: AgentState) -> Optional[IncomingEvent]:
        """Classify and enhance a CloudEvent for better processing"""
        try:
            # Extract CloudEvent data
            cloudevent_data = event.raw_data.get("cloudevent", event.raw_data)
            
            cloudevent_type = cloudevent_data.get("type", "unknown")
            cloudevent_source = cloudevent_data.get("source", "unknown")
            cloudevent_id = cloudevent_data.get("id", event.event_id)
            cloudevent_subject = cloudevent_data.get("subject")
            cloudevent_time_str = cloudevent_data.get("time")
            cloudevent_payload = cloudevent_data.get("data", {})
            
            # Log CloudEvent classification details
            logger.info(f"EventMonitor: Classifying CloudEvent - type='{cloudevent_type}', source='{cloudevent_source}', id='{cloudevent_id}', subject='{cloudevent_subject}', payload={cloudevent_payload}")
            
            # Parse CloudEvent time if available
            cloudevent_time = None
            if cloudevent_time_str:
                try:
                    cloudevent_time = datetime.fromisoformat(cloudevent_time_str.replace('Z', '+00:00'))
                except ValueError:
                    cloudevent_time = None
            
            # Create CloudEvent context
            cloudevent_context = CloudEventContext(
                cloudevent_id=cloudevent_id,
                cloudevent_type=cloudevent_type,
                cloudevent_source=cloudevent_source,
                cloudevent_subject=cloudevent_subject,
                cloudevent_time=cloudevent_time,
                data=cloudevent_payload
            )
            
            # Determine specific trigger type based on CloudEvent type
            specific_trigger = self._map_cloudevent_to_trigger(cloudevent_type)
            
            # Extract Discord context if available
            discord_context = None
            interaction_data = cloudevent_payload.get("interaction_data", {})
            if interaction_data:
                discord_context = DiscordContext(
                    guild_id=interaction_data.get("guild_id"),
                    channel_id=interaction_data.get("channel_id"),
                    user_id=interaction_data.get("user_id"),
                    message_id=cloudevent_payload.get("message_id")
                )
            
            # Extract event context if available  
            event_context = None
            event_data = cloudevent_payload.get("event_data", {})
            if event_data and isinstance(event_data, dict):
                event_context = EventContext(
                    event_id=str(event_data.get("message_id", cloudevent_id)),
                    event_title=event_data.get("topic", "Unknown Event"),
                    event_description=f"Location: {event_data.get('location', 'TBD')}, Time: {event_data.get('time', 'TBD')}",
                    created_by=str(event_data.get("creator_id", "unknown")),
                    location=event_data.get("location"),
                    rsvp_count=0
                )
            
            # Create enhanced event
            enhanced_event = IncomingEvent(
                event_id=cloudevent_id,
                trigger_type=specific_trigger,
                priority=self._determine_priority(cloudevent_type, cloudevent_payload),
                timestamp=cloudevent_time or event.timestamp,
                discord_context=discord_context,
                event_context=event_context,
                cloudevent_context=cloudevent_context,
                raw_data=cloudevent_payload,
                metadata={
                    **event.metadata,
                    "cloudevent_type": cloudevent_type,
                    "cloudevent_source": cloudevent_source,
                    "original_event_id": event.event_id
                }
            )
            
            return enhanced_event
            
        except Exception as e:
            self.log_execution(state, f"Error classifying CloudEvent: {e}", "error")
            return None
    
    def _map_cloudevent_to_trigger(self, cloudevent_type: str) -> EventTriggerType:
        """Map CloudEvent type to specific trigger type"""
        type_mapping = {
            "com.tlt.discord.create-event": EventTriggerType.CLOUDEVENT_CREATE_EVENT,
            "com.tlt.discord.register-guild": EventTriggerType.CLOUDEVENT_REGISTER_GUILD,
            "com.tlt.discord.deregister-guild": EventTriggerType.CLOUDEVENT_DEREGISTER_GUILD,
            "com.tlt.discord.update-event": EventTriggerType.CLOUDEVENT_UPDATE_EVENT,
            "com.tlt.discord.delete-event": EventTriggerType.CLOUDEVENT_DELETE_EVENT,
            "com.tlt.discord.list-events": EventTriggerType.CLOUDEVENT_LIST_EVENTS,
            "com.tlt.discord.event-info": EventTriggerType.CLOUDEVENT_EVENT_INFO,
            "com.tlt.discord.rsvp-event": EventTriggerType.CLOUDEVENT_RSVP_EVENT,
            "com.tlt.discord.photo-vibe-check": EventTriggerType.CLOUDEVENT_PHOTO_VIBE_CHECK,
            "com.tlt.discord.message": EventTriggerType.DISCORD_MESSAGE
        }
        
        return type_mapping.get(cloudevent_type, EventTriggerType.CLOUDEVENT)
    
    def _determine_priority(self, cloudevent_type: str, payload: Dict[str, Any]) -> MessagePriority:
        """Determine event priority based on CloudEvent type and payload"""
        # High priority events
        if cloudevent_type in [
            "com.tlt.discord.create-event",
            "com.tlt.discord.register-guild", 
            "com.tlt.discord.deregister-guild"
        ]:
            return MessagePriority.HIGH
        
        # Normal priority events
        if cloudevent_type in [
            "com.tlt.discord.update-event",
            "com.tlt.discord.delete-event",
            "com.tlt.discord.rsvp-event"
        ]:
            return MessagePriority.NORMAL
        
        # Low priority events
        if cloudevent_type in [
            "com.tlt.discord.list-events",
            "com.tlt.discord.event-info"
        ]:
            return MessagePriority.LOW
        
        # Check payload for priority override
        payload_priority = payload.get("priority", "normal")
        try:
            return MessagePriority(payload_priority.lower())
        except ValueError:
            return MessagePriority.NORMAL