"""CloudEvents CNCF standard models for TLT"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator, field_serializer
from enum import Enum


class ContentType(str, Enum):
    """Supported content types"""
    APPLICATION_JSON = "application/json"
    TEXT_PLAIN = "text/plain"


class TLTEventType(str, Enum):
    """TLT event types following Discord-specific namespace for ambient agent compatibility"""
    CREATE_EVENT = "com.tlt.discord.create-event"
    UPDATE_EVENT = "com.tlt.discord.update-event" 
    DELETE_EVENT = "com.tlt.discord.delete-event"
    RSVP_EVENT = "com.tlt.discord.rsvp-event"
    DISCORD_MESSAGE = "com.tlt.discord.message"
    PHOTO_VIBE_CHECK = "com.tlt.discord.photo-vibe-check"
    VIBE_ACTION = "com.tlt.discord.vibe-action"
    PROMOTION_IMAGE = "com.tlt.discord.promotion-image"
    SAVE_EVENT_TO_GUILD_DATA = "com.tlt.discord.save-event-to-guild-data"
    TIMER_TRIGGER = "com.tlt.discord.timer-trigger"
    MANUAL_TRIGGER = "com.tlt.discord.manual-trigger"
    REGISTER_GUILD = "com.tlt.discord.register-guild"
    DEREGISTER_GUILD = "com.tlt.discord.deregister-guild"
    LIST_EVENTS = "com.tlt.discord.list-events"
    EVENT_INFO = "com.tlt.discord.event-info"


class CloudEvent(BaseModel):
    """
    CloudEvents v1.0 specification implementation
    https://github.com/cloudevents/spec/blob/v1.0/spec.md
    """
    
    # Required attributes
    specversion: str = Field("1.0", description="CloudEvents specification version")
    type: str = Field(..., description="Event type in reverse DNS notation")
    source: str = Field(..., description="Event source URI")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Event identifier")
    
    # Optional attributes
    time: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    datacontenttype: Optional[str] = Field("application/json", description="Content type of data")
    dataschema: Optional[str] = Field(None, description="URI of the schema for data")
    subject: Optional[str] = Field(None, description="Subject of the event")
    
    # Event data
    data: Optional[Dict[str, Any]] = Field(None, description="Event payload")
    
    @validator('time', pre=True)
    def validate_time(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
    @validator('type')
    def validate_type(cls, v):
        if not v.startswith('com.tlt.discord.'):
            raise ValueError("Event type must start with 'com.tlt.discord.'")
        return v
    
    @field_serializer('time')
    def serialize_time(self, value: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to ISO string for JSON compatibility"""
        return value.isoformat() if value else None


class TLTCreateEventData(BaseModel):
    """Data payload for com.tlt.discord.create-event"""
    event_data: Dict[str, Any] = Field(..., description="Event creation data")
    interaction_data: Dict[str, Any] = Field(..., description="Discord interaction context")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTUpdateEventData(BaseModel):
    """Data payload for com.tlt.discord.update-event"""
    event_id: str = Field(..., description="ID of event being updated")
    update_type: str = Field(..., description="Type of update")
    update_data: Dict[str, Any] = Field(..., description="Update payload")
    user_id: Optional[str] = Field(None, description="User making the update")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTRSVPEventData(BaseModel):
    """Data payload for com.tlt.discord.rsvp-event"""
    guild_id: str = Field(..., description="Discord guild ID")
    event_id: str = Field(..., description="ID of event for RSVP")
    user_id: str = Field(..., description="User making RSVP")
    rsvp_type: str = Field(..., description="Type of RSVP (going, not_going, etc.)")
    emoji: Optional[str] = Field(None, description="Emoji used for RSVP")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTDiscordMessageData(BaseModel):
    """Data payload for com.tlt.discord.message"""
    guild_id: str = Field(..., description="Discord guild ID")
    channel_id: str = Field(..., description="Discord channel ID") 
    user_id: str = Field(..., description="Discord user ID")
    message_id: Optional[str] = Field(None, description="Discord message ID")
    content: str = Field(..., description="Message content")
    message_type: str = Field("message", description="Type of message")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTPhotoVibeCheckData(BaseModel):
    """Data payload for com.tlt.discord.photo-vibe-check"""
    guild_id: str = Field(..., description="Discord guild ID or 'dm_channel' for DMs")
    channel_id: str = Field(..., description="Discord channel ID")
    user_id: str = Field(..., description="Discord user ID")
    user_name: str = Field(..., description="Discord user display name")
    event_id: Optional[str] = Field(None, description="Event ID for photo submission")
    photo_url: str = Field(..., description="URL of the submitted photo")
    filename: str = Field(..., description="Original filename of the photo")
    content_type: Optional[str] = Field(None, description="MIME type of the photo")
    size: Optional[int] = Field(None, description="Size of the photo in bytes")
    message_content: Optional[str] = Field(None, description="Message content from user")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTVibeActionData(BaseModel):
    """Data payload for com.tlt.discord.vibe-action"""
    guild_id: str = Field(..., description="Discord guild ID")
    channel_id: str = Field(..., description="Discord channel ID")
    user_id: str = Field(..., description="Discord user ID")
    user_name: str = Field(..., description="Discord user display name")
    event_id: str = Field(..., description="Event ID for vibe action")
    action: str = Field(..., description="Vibe action type (generate_event_slideshow, create_vibe_snapshot, etc.)")
    event_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Event data context")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTPromotionImageData(BaseModel):
    """Data payload for com.tlt.discord.promotion-image"""
    guild_id: str = Field(..., description="Discord guild ID")
    channel_id: str = Field(..., description="Discord channel ID")
    user_id: str = Field(..., description="Discord user ID")
    user_name: str = Field(..., description="Discord user display name")
    event_id: str = Field(..., description="Event ID for promotion image")
    image_url: str = Field(..., description="Original Discord image URL")
    local_path: str = Field(..., description="Local file path where image is stored")
    filename: str = Field(..., description="Original filename of the image")
    content_type: str = Field(..., description="MIME content type of the image")
    size: int = Field(..., description="File size in bytes")
    event_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Event data context")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTSaveEventToGuildDataData(BaseModel):
    """Data payload for com.tlt.discord.save-event-to-guild-data"""
    event_id: str = Field(..., description="Event ID (message ID)")
    guild_id: str = Field(..., description="Discord guild ID")
    event_data: Dict[str, Any] = Field(..., description="Complete event data to save")
    user_id: str = Field(..., description="User who created the event")
    user_name: str = Field(..., description="Name of user who created the event")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTTimerTriggerData(BaseModel):
    """Data payload for com.tlt.discord.timer-trigger"""
    event_id: str = Field(..., description="Event ID for timer")
    timer_type: str = Field(..., description="Type of timer")
    scheduled_time: datetime = Field(..., description="When timer was scheduled")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @field_serializer('scheduled_time')
    def serialize_scheduled_time(self, value: datetime) -> str:
        """Serialize datetime to ISO string for JSON compatibility"""
        return value.isoformat()


class TLTRegisterGuildData(BaseModel):
    """Data payload for com.tlt.discord.register-guild"""
    guild_id: str = Field(..., description="Discord guild ID")
    guild_name: str = Field(..., description="Discord guild name")
    user_id: str = Field(..., description="User registering the guild")
    user_name: str = Field(..., description="Username of registering user")
    channel_id: str = Field(..., description="Channel where command was executed")
    channel_name: str = Field(..., description="Channel name")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTDeregisterGuildData(BaseModel):
    """Data payload for com.tlt.discord.deregister-guild"""
    guild_id: str = Field(..., description="Discord guild ID")
    guild_name: str = Field(..., description="Discord guild name")
    user_id: str = Field(..., description="User deregistering the guild")
    user_name: str = Field(..., description="Username of deregistering user")
    channel_id: str = Field(..., description="Channel where command was executed")
    channel_name: str = Field(..., description="Channel name")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTListEventsData(BaseModel):
    """Data payload for com.tlt.discord.list-events"""
    guild_id: str = Field(..., description="Discord guild ID")
    channel_id: str = Field(..., description="Channel where list was requested")
    user_id: str = Field(..., description="User requesting the list")
    user_name: str = Field(..., description="Username of requesting user")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTEventInfoData(BaseModel):
    """Data payload for com.tlt.discord.event-info"""
    guild_id: str = Field(..., description="Discord guild ID")
    channel_id: str = Field(..., description="Channel where info was requested")
    user_id: str = Field(..., description="User requesting info")
    user_name: str = Field(..., description="Username of requesting user")
    event_id: str = Field(..., description="ID of event to get info for")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TLTDeleteEventData(BaseModel):
    """Data payload for com.tlt.discord.delete-event"""
    guild_id: str = Field(..., description="Discord guild ID")
    channel_id: str = Field(..., description="Channel where event was deleted")
    user_id: str = Field(..., description="User deleting the event")
    user_name: str = Field(..., description="Username of deleting user")
    event_id: str = Field(..., description="ID of event to delete")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


def create_discord_source(guild_id: str, channel_id: str) -> str:
    """Create a Discord source URI following CloudEvents format"""
    return f"/discord/{guild_id}/{channel_id}"


def create_create_event_cloudevent(
    guild_id: str,
    channel_id: str,
    event_data: Dict[str, Any],
    interaction_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
    event_id: Optional[str] = None,
    subject: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for event creation from Discord"""
    
    data = TLTCreateEventData(
        event_data=event_data,
        interaction_data=interaction_data,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.CREATE_EVENT,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=subject or f"event-creation-{interaction_data.get('user_id', 'unknown')}"
    )
    
    if event_id:
        cloud_event.id = event_id
    
    return cloud_event


def create_discord_message_cloudevent(
    guild_id: str,
    channel_id: str,
    user_id: str,
    content: str,
    message_id: Optional[str] = None,
    message_type: str = "message",
    metadata: Optional[Dict[str, Any]] = None,
    event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for Discord message"""
    
    data = TLTDiscordMessageData(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        message_id=message_id,
        content=content,
        message_type=message_type,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.DISCORD_MESSAGE,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"message-{user_id}"
    )
    
    if event_id:
        cloud_event.id = event_id
    
    return cloud_event


def create_update_event_cloudevent(
    guild_id: str,
    channel_id: str,
    event_id: str,
    update_type: str,
    update_data: Dict[str, Any],
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for event update"""
    
    data = TLTUpdateEventData(
        event_id=event_id,
        update_type=update_type,
        update_data=update_data,
        user_id=user_id,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.UPDATE_EVENT,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"event-{event_id}-update"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_timer_trigger_cloudevent(
    guild_id: str,
    channel_id: str,
    event_id: str,
    timer_type: str,
    scheduled_time: datetime,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for timer trigger"""
    
    data = TLTTimerTriggerData(
        event_id=event_id,
        timer_type=timer_type,
        scheduled_time=scheduled_time,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.TIMER_TRIGGER,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"timer-{event_id}-{timer_type}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_register_guild_cloudevent(
    guild_id: str,
    guild_name: str,
    channel_id: str,
    channel_name: str,
    user_id: str,
    user_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for guild registration"""
    
    data = TLTRegisterGuildData(
        guild_id=guild_id,
        guild_name=guild_name,
        user_id=user_id,
        user_name=user_name,
        channel_id=channel_id,
        channel_name=channel_name,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.REGISTER_GUILD,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"register-guild-{guild_id}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_deregister_guild_cloudevent(
    guild_id: str,
    guild_name: str,
    channel_id: str,
    channel_name: str,
    user_id: str,
    user_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for guild deregistration"""
    
    data = TLTDeregisterGuildData(
        guild_id=guild_id,
        guild_name=guild_name,
        user_id=user_id,
        user_name=user_name,
        channel_id=channel_id,
        channel_name=channel_name,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.DEREGISTER_GUILD,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"deregister-guild-{guild_id}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_list_events_cloudevent(
    guild_id: str,
    channel_id: str,
    user_id: str,
    user_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for listing events"""
    
    data = TLTListEventsData(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        user_name=user_name,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.LIST_EVENTS,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"list-events-{user_id}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_event_info_cloudevent(
    guild_id: str,
    channel_id: str,
    user_id: str,
    user_name: str,
    event_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for event info request"""
    
    data = TLTEventInfoData(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        user_name=user_name,
        event_id=event_id,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.EVENT_INFO,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"event-info-{event_id}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_delete_event_cloudevent(
    guild_id: str,
    channel_id: str,
    user_id: str,
    user_name: str,
    event_id: str,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for event deletion"""
    
    data = TLTDeleteEventData(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        user_name=user_name,
        event_id=event_id,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.DELETE_EVENT,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"delete-event-{event_id}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_rsvp_event_cloudevent(
    guild_id: str,
    channel_id: str,
    event_id: str,
    user_id: str,
    user_name: str,
    rsvp_type: str,
    action: str,
    emoji: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for RSVP reaction"""
    
    data = TLTRSVPEventData(
        guild_id=guild_id,
        event_id=event_id,
        user_id=user_id,
        rsvp_type=rsvp_type,
        emoji=emoji,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.RSVP_EVENT,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"rsvp-{event_id}-{user_id}-{action}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_photo_vibe_check_cloudevent(
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
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for photo vibe check submission"""
    
    data = TLTPhotoVibeCheckData(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        user_name=user_name,
        event_id=event_id,
        photo_url=photo_url,
        filename=filename,
        content_type=content_type,
        size=size,
        message_content=message_content,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.PHOTO_VIBE_CHECK,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"photo-vibe-check-{user_id}-{filename}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_vibe_action_cloudevent(
    guild_id: str,
    channel_id: str,
    user_id: str,
    user_name: str,
    event_id: str,
    action: str,
    event_data: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for vibe action submission"""
    
    data = TLTVibeActionData(
        guild_id=guild_id,
        channel_id=channel_id,
        user_id=user_id,
        user_name=user_name,
        event_id=event_id,
        action=action,
        event_data=event_data or {},
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.VIBE_ACTION,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"vibe-action-{user_id}-{action}-{event_id}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_promotion_image_cloudevent(
    guild_id: str,
    channel_id: str,
    user_id: str,
    user_name: str,
    event_id: str,
    image_url: str,
    local_path: str,
    filename: str,
    content_type: str,
    size: int,
    event_data: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for promotion image upload"""
    
    data = TLTPromotionImageData(
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
    
    cloud_event = CloudEvent(
        type=TLTEventType.PROMOTION_IMAGE,
        source=create_discord_source(guild_id, channel_id),
        data=data.model_dump(),
        subject=f"promotion-image-{user_id}-{event_id}-{filename}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event


def create_save_event_to_guild_data_cloudevent(
    event_id: str,
    guild_id: str,
    event_data: Dict[str, Any],
    user_id: str,
    user_name: str,
    metadata: Optional[Dict[str, Any]] = None,
    cloud_event_id: Optional[str] = None
) -> CloudEvent:
    """Create a CloudEvent for saving event data to guild_data directory"""
    
    data = TLTSaveEventToGuildDataData(
        event_id=event_id,
        guild_id=guild_id,
        event_data=event_data,
        user_id=user_id,
        user_name=user_name,
        metadata=metadata or {}
    )
    
    cloud_event = CloudEvent(
        type=TLTEventType.SAVE_EVENT_TO_GUILD_DATA,
        source=create_discord_source(guild_id, event_id),
        data=data.model_dump(),
        subject=f"save-event-{guild_id}-{event_id}"
    )
    
    if cloud_event_id:
        cloud_event.id = cloud_event_id
    
    return cloud_event
