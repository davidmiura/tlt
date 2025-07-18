"""Guild Manager tools registration"""

import os
from typing import Dict, Any, Optional
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.guild_manager.service import GuildManagerService
from tlt.mcp_services.guild_manager.models import (
    RegisterGuildResult,
    DeregisterGuildResult,
    GetGuildInfoResult,
    ListGuildsResult,
    UpdateGuildSettingsResult,
    GetGuildStatsResult
)
from tlt.shared.user_state_manager import UserStateManager
from tlt.shared.event_state_manager import EventStateManager

def register_tools(mcp: FastMCP, service: GuildManagerService):
    """Register all guild manager tools"""
    
    # Initialize state managers
    guild_data_dir = os.getenv('GUILD_DATA_DIR', './guild_data')
    data_dir = os.path.join(guild_data_dir, 'data')
    user_state_manager = UserStateManager(data_dir)
    event_state_manager = EventStateManager(data_dir)
    
    @mcp.tool()
    async def register_guild(
        guild_id: str,
        guild_name: str,
        channel_id: str,
        channel_name: str,
        user_id: str,
        user_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register a Discord guild for TLT events"""
        try:
            result = await service.register_guild(
                guild_id=guild_id,
                guild_name=guild_name,
                channel_id=channel_id,
                channel_name=channel_name,
                user_id=user_id,
                user_name=user_name,
                metadata=metadata
            )
            
            if result.get('success'):
                logger.info(f"Guild registered successfully: {guild_id} ({guild_name}) by {user_id} ({user_name})")
                
                # Update event.json with guild registration
                event_state_manager.update_nested_field(guild_id, "guild_registration", "guild_registered", True)
                event_state_manager.update_nested_field(guild_id, "guild_registration", "guild_name", guild_name)
                event_state_manager.update_nested_field(guild_id, "guild_registration", "channel_id", channel_id)
                event_state_manager.update_nested_field(guild_id, "guild_registration", "channel_name", channel_name)
                event_state_manager.update_nested_field(guild_id, "guild_registration", "registered_by", {
                    "user_id": user_id,
                    "user_name": user_name
                })
            else:
                logger.error(f"Failed to register guild {guild_id}: {result.get('error', 'Unknown error')}")
            
            # Save result to UserStateManager
            register_result = RegisterGuildResult(
                success=result.get('success', False),
                message=result.get('message'),
                guild_id=guild_id,
                guild_name=guild_name,
                channel_id=channel_id,
                channel_name=channel_name,
                user_id=user_id,
                user_name=user_name,
                metadata=metadata,
                error=result.get('error')
            )
            user_state_manager.add_model_entry(guild_id, "guild_registration", user_id, register_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error registering guild {guild_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                register_result = RegisterGuildResult(
                    success=False,
                    error=str(e),
                    guild_id=guild_id,
                    guild_name=guild_name,
                    channel_id=channel_id,
                    channel_name=channel_name,
                    user_id=user_id,
                    user_name=user_name,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, "guild_registration", user_id, register_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    async def deregister_guild(
        guild_id: str,
        guild_name: str,
        user_id: str,
        user_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Deregister a Discord guild from TLT events"""
        try:
            result = await service.deregister_guild(
                guild_id=guild_id,
                guild_name=guild_name,
                user_id=user_id,
                user_name=user_name,
                metadata=metadata
            )
            
            if result.get('success'):
                logger.info(f"Guild deregistered successfully: {guild_id} ({guild_name}) by {user_id} ({user_name})")
                
                # Update event.json with guild deregistration
                event_state_manager.update_nested_field(guild_id, "guild_registration", "guild_registered", False)
                event_state_manager.update_nested_field(guild_id, "guild_registration", "deregistered_by", {
                    "user_id": user_id,
                    "user_name": user_name
                })
                event_state_manager.append_to_array_field(guild_id, "guild_registration", "deregistration_history", {
                    "user_id": user_id,
                    "user_name": user_name,
                    "deregistered_at": result.get('timestamp', 'unknown')
                })
            else:
                logger.error(f"Failed to deregister guild {guild_id}: {result.get('error', 'Unknown error')}")
            
            # Save result to UserStateManager
            deregister_result = DeregisterGuildResult(
                success=result.get('success', False),
                message=result.get('message'),
                guild_id=guild_id,
                guild_name=guild_name,
                user_id=user_id,
                user_name=user_name,
                metadata=metadata,
                error=result.get('error')
            )
            user_state_manager.add_model_entry(guild_id, "guild_registration", user_id, deregister_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error deregistering guild {guild_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                deregister_result = DeregisterGuildResult(
                    success=False,
                    error=str(e),
                    guild_id=guild_id,
                    guild_name=guild_name,
                    user_id=user_id,
                    user_name=user_name,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, "guild_registration", user_id, deregister_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    async def get_guild_info(guild_id: str) -> Dict[str, Any]:
        """Get information about a registered guild"""
        try:
            result = await service.get_guild_info(guild_id=guild_id)
            
            if result.get('success'):
                logger.info(f"Guild info retrieved successfully: {guild_id}")
            else:
                logger.error(f"Failed to get guild info for {guild_id}: {result.get('error', 'Unknown error')}")
            
            # Save result to UserStateManager
            guild_info_result = GetGuildInfoResult(
                success=result.get('success', False),
                message=result.get('message'),
                guild_id=guild_id,
                guild_info=result.get('guild_info'),
                error=result.get('error')
            )
            user_state_manager.add_model_entry(guild_id, "guild_info", "system", guild_info_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting guild info for {guild_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_info_result = GetGuildInfoResult(
                    success=False,
                    error=str(e),
                    guild_id=guild_id
                )
                user_state_manager.add_model_entry(guild_id, "guild_info", "system", guild_info_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    async def list_guilds(status: Optional[str] = None) -> Dict[str, Any]:
        """List all registered guilds, optionally filtered by status"""
        try:
            result = await service.list_guilds(status=status)
            
            if result.get('success'):
                guild_count = len(result.get('guilds', []))
                logger.info(f"Guilds listed successfully: {guild_count} guilds (status: {status or 'all'})")
            else:
                logger.error(f"Failed to list guilds: {result.get('error', 'Unknown error')}")
            
            # Save result to UserStateManager (use "all_guilds" as guild_id for global operations)
            list_guilds_result = ListGuildsResult(
                success=result.get('success', False),
                message=result.get('message'),
                guilds=result.get('guilds'),
                guild_count=len(result.get('guilds', [])) if result.get('guilds') else None,
                status_filter=status,
                error=result.get('error')
            )
            user_state_manager.add_model_entry("all_guilds", "guild_listing", "system", list_guilds_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing guilds: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                list_guilds_result = ListGuildsResult(
                    success=False,
                    error=str(e),
                    status_filter=status
                )
                user_state_manager.add_model_entry("all_guilds", "guild_listing", "system", list_guilds_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    async def update_guild_settings(
        guild_id: str,
        settings: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Update settings for a registered guild"""
        try:
            result = await service.update_guild_settings(
                guild_id=guild_id,
                settings=settings,
                user_id=user_id
            )
            
            if result.get('success'):
                logger.info(f"Guild settings updated successfully: {guild_id} by {user_id}")
                
                # Update event.json with guild settings
                for setting_key, setting_value in settings.items():
                    event_state_manager.update_nested_field(guild_id, "guild_settings", f"guild_settings.{setting_key}", setting_value)
                
                # Track settings update history
                event_state_manager.append_to_array_field(guild_id, "guild_settings", "settings_update_history", {
                    "user_id": user_id,
                    "updated_settings": settings,
                    "updated_at": result.get('timestamp', 'unknown')
                })
            else:
                logger.error(f"Failed to update guild settings for {guild_id}: {result.get('error', 'Unknown error')}")
            
            # Save result to UserStateManager
            update_settings_result = UpdateGuildSettingsResult(
                success=result.get('success', False),
                message=result.get('message'),
                guild_id=guild_id,
                settings=settings,
                user_id=user_id,
                updated_settings=result.get('updated_settings'),
                error=result.get('error')
            )
            user_state_manager.add_model_entry(guild_id, "guild_settings", user_id, update_settings_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating guild settings for {guild_id}: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                update_settings_result = UpdateGuildSettingsResult(
                    success=False,
                    error=str(e),
                    guild_id=guild_id,
                    settings=settings,
                    user_id=user_id
                )
                user_state_manager.add_model_entry(guild_id, "guild_settings", user_id, update_settings_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    async def get_guild_stats() -> Dict[str, Any]:
        """Get statistics about registered guilds"""
        try:
            result = await service.get_guild_stats()
            
            if result.get('success'):
                total_guilds = result.get('stats', {}).get('total_guilds', 0)
                logger.info(f"Guild stats retrieved successfully: {total_guilds} total guilds")
            else:
                logger.error(f"Failed to get guild stats: {result.get('error', 'Unknown error')}")
            
            # Save result to UserStateManager (use "all_guilds" as guild_id for global operations)
            guild_stats_result = GetGuildStatsResult(
                success=result.get('success', False),
                message=result.get('message'),
                stats=result.get('stats'),
                error=result.get('error')
            )
            user_state_manager.add_model_entry("all_guilds", "guild_stats", "system", guild_stats_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting guild stats: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_stats_result = GetGuildStatsResult(
                    success=False,
                    error=str(e)
                )
                user_state_manager.add_model_entry("all_guilds", "guild_stats", "system", guild_stats_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    logger.info("Guild Manager tools registered successfully")