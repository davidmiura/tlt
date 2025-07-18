"""Guild Manager data models"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class GuildRegistrationData(BaseModel):
    """Data model for guild registration"""
    guild_id: str
    guild_name: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class GuildSettings(BaseModel):
    """Guild settings model"""
    auto_reminders: bool = True
    vibe_check_enabled: bool = True
    canvas_enabled: bool = True
    photo_collection_enabled: bool = True

class RegisteredGuild(BaseModel):
    """Model for a registered guild"""
    guild_id: str
    guild_name: str
    channel_id: str
    channel_name: str
    registered_by: Dict[str, str]
    registered_at: datetime
    status: str = "active"
    settings: GuildSettings = Field(default_factory=GuildSettings)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GuildStats(BaseModel):
    """Guild statistics model"""
    total_guilds: int
    active_guilds: int
    guilds_by_status: Dict[str, int]
    settings_summary: Dict[str, int]

# Tool Result Models for UserStateManager
class RegisterGuildResult(BaseModel):
    """Result model for register_guild tool"""
    success: bool
    message: Optional[str] = None
    guild_id: str
    guild_name: str
    channel_id: str
    channel_name: str
    user_id: str
    user_name: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DeregisterGuildResult(BaseModel):
    """Result model for deregister_guild tool"""
    success: bool
    message: Optional[str] = None
    guild_id: str
    guild_name: str
    user_id: str
    user_name: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GetGuildInfoResult(BaseModel):
    """Result model for get_guild_info tool"""
    success: bool
    message: Optional[str] = None
    guild_id: str
    guild_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ListGuildsResult(BaseModel):
    """Result model for list_guilds tool"""
    success: bool
    message: Optional[str] = None
    guilds: Optional[list] = None
    guild_count: Optional[int] = None
    status_filter: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UpdateGuildSettingsResult(BaseModel):
    """Result model for update_guild_settings tool"""
    success: bool
    message: Optional[str] = None
    guild_id: str
    settings: Dict[str, Any]
    user_id: str
    updated_settings: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GetGuildStatsResult(BaseModel):
    """Result model for get_guild_stats tool"""
    success: bool
    message: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))