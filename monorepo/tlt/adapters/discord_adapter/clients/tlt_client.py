"""TLT Service client for Discord Adapter"""

import os
import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import sys
import os as path_os

# Add project root to path for shared imports
project_root = path_os.path.dirname(path_os.path.dirname(path_os.path.dirname(path_os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from tlt.shared.cloudevents import (
    CloudEvent, 
    create_create_event_cloudevent,
    create_discord_message_cloudevent,
    create_update_event_cloudevent,
    create_timer_trigger_cloudevent,
    create_register_guild_cloudevent,
    create_deregister_guild_cloudevent,
    create_list_events_cloudevent,
    create_event_info_cloudevent,
    create_delete_event_cloudevent,
    create_rsvp_event_cloudevent,
    create_photo_vibe_check_cloudevent,
    create_vibe_action_cloudevent,
    create_save_event_to_guild_data_cloudevent
)

logger = logging.getLogger(__name__)

class TLTServiceClient:
    """Client for communicating with TLT Service"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("TLT_SERVICE_URL", "http://localhost:8008")
        self.timeout = 30.0
        
        logger.info(f"TLT Service client initialized with base URL: {self.base_url}")
    
    async def send_discord_message(
        self,
        guild_id: str,
        channel_id: str,
        user_id: str,
        content: str,
        message_id: str = None,
        message_type: str = "message",
        priority: str = "normal",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Send a Discord message to TLT service for processing using CloudEvents"""
        try:
            # Create CloudEvent for Discord message
            cloud_event = create_discord_message_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                content=content,
                message_id=message_id,
                message_type=message_type,
                metadata=metadata or {}
            )
            
            logger.info(f"Created CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the new /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Discord CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Discord CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Discord CloudEvent to TLT service: {e}")
            return None
    
    async def create_event(
        self,
        event_data: Dict[str, Any],
        interaction_data: Dict[str, Any],
        message_id: str = None,
        priority: str = "normal",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Send event creation data to TLT service for processing using CloudEvents"""
        try:
            # Extract guild and channel info for CloudEvents source
            guild_id = interaction_data.get("guild_id", "unknown")
            channel_id = interaction_data.get("channel_id", "unknown")
            
            # Create CloudEvent
            cloud_event = create_create_event_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                event_data=event_data,
                interaction_data=interaction_data,
                metadata=metadata or {},
                subject=f"create-event-{interaction_data.get('user_id', 'unknown')}"
            )
            
            logger.info(f"Created CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the new /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending CloudEvent to TLT service: {e}")
            return None

    async def send_event_update(
        self,
        event_id: str,
        update_type: str,
        data: Dict[str, Any],
        guild_id: str,
        channel_id: str,
        user_id: str = None,
        priority: str = "normal",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Send an event update to TLT service for processing using CloudEvents"""
        try:
            # Create CloudEvent for event update
            cloud_event = create_update_event_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                event_id=event_id,
                update_type=update_type,
                update_data=data,
                user_id=user_id,
                metadata=metadata or {}
            )
            
            logger.info(f"Created Update CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the new /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Update CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Update CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Update CloudEvent to TLT service: {e}")
            return None
    
    async def schedule_timer(
        self,
        event_id: str,
        timer_type: str,
        scheduled_time: datetime,
        guild_id: str,
        channel_id: str,
        priority: str = "normal",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Schedule a timer through TLT service using CloudEvents"""
        try:
            # Create CloudEvent for timer trigger
            cloud_event = create_timer_trigger_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                event_id=event_id,
                timer_type=timer_type,
                scheduled_time=scheduled_time,
                metadata=metadata or {}
            )
            
            logger.info(f"Created Timer CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the new /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Timer CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Timer CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Timer CloudEvent to TLT service: {e}")
            return None
    
    async def register_guild(
        self,
        guild_id: str,
        guild_name: str,
        channel_id: str,
        channel_name: str,
        user_id: str,
        user_name: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Register a guild using CloudEvents"""
        try:
            # Create CloudEvent for guild registration
            cloud_event = create_register_guild_cloudevent(
                guild_id=guild_id,
                guild_name=guild_name,
                channel_id=channel_id,
                channel_name=channel_name,
                user_id=user_id,
                user_name=user_name,
                metadata=metadata or {}
            )
            
            logger.info(f"Created Register Guild CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Register Guild CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Register Guild CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Register Guild CloudEvent to TLT service: {e}")
            return None
    
    async def deregister_guild(
        self,
        guild_id: str,
        guild_name: str,
        channel_id: str,
        channel_name: str,
        user_id: str,
        user_name: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Deregister a guild using CloudEvents"""
        try:
            # Create CloudEvent for guild deregistration
            cloud_event = create_deregister_guild_cloudevent(
                guild_id=guild_id,
                guild_name=guild_name,
                channel_id=channel_id,
                channel_name=channel_name,
                user_id=user_id,
                user_name=user_name,
                metadata=metadata or {}
            )
            
            logger.info(f"Created Deregister Guild CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Deregister Guild CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Deregister Guild CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Deregister Guild CloudEvent to TLT service: {e}")
            return None
    
    async def list_events(
        self,
        guild_id: str,
        channel_id: str,
        user_id: str,
        user_name: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """List events using CloudEvents"""
        try:
            # Create CloudEvent for listing events
            cloud_event = create_list_events_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                user_name=user_name,
                metadata=metadata or {}
            )
            
            logger.info(f"Created List Events CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"List Events CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending List Events CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending List Events CloudEvent to TLT service: {e}")
            return None
    
    async def get_event_info(
        self,
        guild_id: str,
        channel_id: str,
        user_id: str,
        user_name: str,
        event_id: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Get event info using CloudEvents"""
        try:
            # Create CloudEvent for event info
            cloud_event = create_event_info_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                user_name=user_name,
                event_id=event_id,
                metadata=metadata or {}
            )
            
            logger.info(f"Created Event Info CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Event Info CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Event Info CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Event Info CloudEvent to TLT service: {e}")
            return None
    
    async def delete_event(
        self,
        guild_id: str,
        channel_id: str,
        user_id: str,
        user_name: str,
        event_id: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Delete event using CloudEvents"""
        try:
            # Create CloudEvent for event deletion
            cloud_event = create_delete_event_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                user_name=user_name,
                event_id=event_id,
                metadata=metadata or {}
            )
            
            logger.info(f"Created Delete Event CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Delete Event CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Delete Event CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Delete Event CloudEvent to TLT service: {e}")
            return None
    
    async def send_rsvp_event(
        self,
        guild_id: str,
        channel_id: str,
        event_id: str,
        user_id: str,
        user_name: str,
        rsvp_type: str,
        action: str,
        emoji: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Send RSVP event using CloudEvents"""
        try:
            # Create CloudEvent for RSVP
            cloud_event = create_rsvp_event_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                event_id=event_id,
                user_id=user_id,
                user_name=user_name,
                rsvp_type=rsvp_type,
                action=action,
                emoji=emoji,
                metadata=metadata or {}
            )
            
            logger.info(f"Created RSVP Event CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"RSVP Event CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending RSVP Event CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending RSVP Event CloudEvent to TLT service: {e}")
            return None
    
    async def send_photo_vibe_check(
        self,
        guild_id: str,
        channel_id: str,
        user_id: str,
        user_name: str,
        photo_url: str,
        filename: str,
        event_id: Optional[str] = None,
        content_type: Optional[str] = None,
        size: Optional[int] = None,
        message_content: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Send photo vibe check submission using CloudEvents"""
        try:
            # Create CloudEvent for photo vibe check
            cloud_event = create_photo_vibe_check_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                user_name=user_name,
                photo_url=photo_url,
                filename=filename,
                event_id=event_id,
                content_type=content_type,
                size=size,
                message_content=message_content,
                metadata=metadata or {}
            )
            
            logger.info(f"Created Photo Vibe Check CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Photo Vibe Check CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Photo Vibe Check CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Photo Vibe Check CloudEvent to TLT service: {e}")
            return None
    
    async def send_vibe_action(
        self,
        guild_id: str,
        channel_id: str,
        user_id: str,
        user_name: str,
        event_id: str,
        action: str,
        event_data: Optional[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Send vibe action request using CloudEvents"""
        try:
            # Create CloudEvent for vibe action
            cloud_event = create_vibe_action_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                user_name=user_name,
                event_id=event_id,
                action=action,
                event_data=event_data or {},
                metadata=metadata or {}
            )
            
            logger.info(f"Created Vibe Action CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Vibe Action CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Vibe Action CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Vibe Action CloudEvent to TLT service: {e}")
            return None
    
    async def send_promotion_image(
        self,
        guild_id: str,
        channel_id: str,
        user_id: str,
        user_name: str,
        event_id: str,
        image_url: str,
        local_path: str,
        event_data: Optional[Dict[str, Any]] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Send promotion image upload request using CloudEvents"""
        try:
            # Extract filename, content_type, and size from metadata
            filename = metadata.get("filename", "unknown.jpg") if metadata else "unknown.jpg"
            content_type = metadata.get("content_type", "image/jpeg") if metadata else "image/jpeg"
            size = metadata.get("size", 0) if metadata else 0
            
            # Create CloudEvent for promotion image upload
            from tlt.shared.cloudevents import create_promotion_image_cloudevent
            cloud_event = create_promotion_image_cloudevent(
                guild_id=guild_id,
                channel_id=channel_id,
                user_id=user_id,
                user_name=user_name,
                event_id=event_id,
                image_url=image_url,
                local_path=local_path,
                filename=filename,
                content_type=content_type,
                size=size,
                event_data=event_data or {},
                metadata=metadata or {}
            )
            
            logger.info(f"Created Promotion Image CloudEvent: type={cloud_event.type}, source={cloud_event.source}, id={cloud_event.id}")
            
            # Send CloudEvent directly to the /cloudevents endpoint
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/cloudevents",
                    json=cloud_event.model_dump(),
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                cloudevent_id = result.get("cloudevent_id")
                
                logger.info(f"Promotion Image CloudEvent sent to TLT service /cloudevents endpoint, id: {cloudevent_id}")
                return cloudevent_id
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error sending Promotion Image CloudEvent to TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error sending Promotion Image CloudEvent to TLT service: {e}")
            return None
    
    async def save_event_to_guild_data(
        self,
        event_id: str,
        guild_id: str,
        event_data: Dict[str, Any],
        user_id: str,
        user_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        priority: str = "normal"
    ) -> Optional[str]:
        """Send a CloudEvent to save event data to guild_data directory"""
        try:
            cloud_event = create_save_event_to_guild_data_cloudevent(
                event_id=event_id,
                guild_id=guild_id,
                event_data=event_data,
                user_id=user_id,
                user_name=user_name,
                metadata=metadata or {}
            )
            
            task_id = await self._send_cloudevent(cloud_event, priority)
            
            if task_id:
                logger.info(f"Save Event to Guild Data CloudEvent sent successfully: {task_id}")
                return task_id
            else:
                logger.error("Failed to send Save Event to Guild Data CloudEvent")
                return None
                
        except Exception as e:
            logger.error(f"Error sending Save Event to Guild Data CloudEvent to TLT service: {e}")
            return None
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a task"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/monitor/tasks/{task_id}"
                )
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Task {task_id} not found")
                return None
            logger.error(f"HTTP error getting task status from TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting task status from TLT service: {e}")
            return None
    
    async def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed task"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/events/task/{task_id}/result"
                )
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Task {task_id} not found")
                return None
            logger.error(f"HTTP error getting task result from TLT service: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting task result from TLT service: {e}")
            return None
    
    async def get_service_status(self) -> Optional[Dict[str, Any]]:
        """Get TLT service status"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/monitor/status")
                response.raise_for_status()
                
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting TLT service status: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting TLT service status: {e}")
            return None
    
    async def health_check(self) -> bool:
        """Check if TLT service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                return response.status_code == 200
                
        except Exception as e:
            logger.error(f"TLT service health check failed: {e}")
            return False

# Global client instance
tlt_client = TLTServiceClient()