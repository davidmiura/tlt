"""Guild Manager Service - handles Discord guild registration and management"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from loguru import logger
from pathlib import Path

class GuildManagerService:
    """Service for managing Discord guild registration and settings"""
    
    def __init__(self):
        self.data_dir = Path(os.getenv('GUILD_DATA_DIR', './guild_data'))
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.guilds_file = self.data_dir / 'guilds.json'
        self.settings_file = self.data_dir / 'settings.json'
        
        # Initialize data files
        self._init_data_files()
        
        logger.info("Guild Manager Service initialized")
    
    def _init_data_files(self):
        """Initialize data files if they don't exist"""
        if not self.guilds_file.exists():
            self._save_guilds({})
        
        if not self.settings_file.exists():
            self._save_settings({})
    
    def _load_guilds(self) -> Dict[str, Any]:
        """Load guilds data from file"""
        try:
            with open(self.guilds_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading guilds data: {e}")
            return {}
    
    def _save_guilds(self, guilds: Dict[str, Any]):
        """Save guilds data to file"""
        try:
            with open(self.guilds_file, 'w') as f:
                json.dump(guilds, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving guilds data: {e}")
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings data from file"""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading settings data: {e}")
            return {}
    
    def _save_settings(self, settings: Dict[str, Any]):
        """Save settings data to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving settings data: {e}")
    
    async def register_guild(self, 
                           guild_id: str, 
                           guild_name: str,
                           channel_id: str,
                           channel_name: str,
                           user_id: str,
                           user_name: str,
                           metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Register a guild for TLT events"""
        try:
            guilds = self._load_guilds()
            
            # Check if guild already registered
            if guild_id in guilds:
                logger.warning(f"Guild {guild_id} already registered")
                return {
                    "success": False,
                    "message": f"Guild {guild_name} is already registered",
                    "guild_id": guild_id,
                    "already_registered": True
                }
            
            # Register guild
            guild_data = {
                "guild_id": guild_id,
                "guild_name": guild_name,
                "channel_id": channel_id,
                "channel_name": channel_name,
                "registered_by": {
                    "user_id": user_id,
                    "user_name": user_name
                },
                "registered_at": datetime.now(timezone.utc).isoformat(),
                "status": "active",
                "settings": {
                    "auto_reminders": True,
                    "vibe_check_enabled": True,
                    "canvas_enabled": True,
                    "photo_collection_enabled": True
                },
                "metadata": metadata or {}
            }
            
            guilds[guild_id] = guild_data
            self._save_guilds(guilds)
            
            logger.info(f"Guild {guild_name} ({guild_id}) registered successfully")
            
            return {
                "success": True,
                "message": f"Guild {guild_name} registered successfully",
                "guild_id": guild_id,
                "guild_data": guild_data
            }
            
        except Exception as e:
            logger.error(f"Error registering guild {guild_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to register guild: {str(e)}",
                "guild_id": guild_id
            }
    
    async def deregister_guild(self,
                             guild_id: str,
                             guild_name: str,
                             user_id: str,
                             user_name: str,
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Deregister a guild from TLT events"""
        try:
            guilds = self._load_guilds()
            
            # Check if guild exists
            if guild_id not in guilds:
                logger.warning(f"Guild {guild_id} not registered")
                return {
                    "success": False,
                    "message": f"Guild {guild_name} is not registered",
                    "guild_id": guild_id,
                    "not_registered": True
                }
            
            # Get guild data for archival
            guild_data = guilds[guild_id]
            
            # Update guild data with deregistration info
            guild_data.update({
                "status": "deregistered",
                "deregistered_by": {
                    "user_id": user_id,
                    "user_name": user_name
                },
                "deregistered_at": datetime.now(timezone.utc).isoformat(),
                "deregistration_metadata": metadata or {}
            })
            
            # Remove from active guilds
            del guilds[guild_id]
            self._save_guilds(guilds)
            
            # Archive guild data
            await self._archive_guild_data(guild_id, guild_data)
            
            logger.info(f"Guild {guild_name} ({guild_id}) deregistered successfully")
            
            return {
                "success": True,
                "message": f"Guild {guild_name} deregistered successfully",
                "guild_id": guild_id,
                "archived_data": guild_data
            }
            
        except Exception as e:
            logger.error(f"Error deregistering guild {guild_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to deregister guild: {str(e)}",
                "guild_id": guild_id
            }
    
    async def get_guild_info(self, guild_id: str) -> Dict[str, Any]:
        """Get information about a registered guild"""
        try:
            guilds = self._load_guilds()
            
            if guild_id not in guilds:
                return {
                    "success": False,
                    "message": "Guild not found",
                    "guild_id": guild_id,
                    "registered": False
                }
            
            guild_data = guilds[guild_id]
            
            return {
                "success": True,
                "guild_id": guild_id,
                "guild_data": guild_data,
                "registered": True
            }
            
        except Exception as e:
            logger.error(f"Error getting guild info {guild_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to get guild info: {str(e)}",
                "guild_id": guild_id
            }
    
    async def list_guilds(self, status: Optional[str] = None) -> Dict[str, Any]:
        """List all registered guilds"""
        try:
            guilds = self._load_guilds()
            
            # Filter by status if specified
            if status:
                filtered_guilds = {
                    gid: data for gid, data in guilds.items() 
                    if data.get("status") == status
                }
            else:
                filtered_guilds = guilds
            
            return {
                "success": True,
                "guilds": filtered_guilds,
                "total_count": len(filtered_guilds),
                "status_filter": status
            }
            
        except Exception as e:
            logger.error(f"Error listing guilds: {e}")
            return {
                "success": False,
                "message": f"Failed to list guilds: {str(e)}"
            }
    
    async def update_guild_settings(self,
                                  guild_id: str,
                                  settings: Dict[str, Any],
                                  user_id: str) -> Dict[str, Any]:
        """Update guild settings"""
        try:
            guilds = self._load_guilds()
            
            if guild_id not in guilds:
                return {
                    "success": False,
                    "message": "Guild not found",
                    "guild_id": guild_id
                }
            
            # Update settings
            guild_data = guilds[guild_id]
            guild_data["settings"].update(settings)
            guild_data["last_updated"] = datetime.now(timezone.utc).isoformat()
            guild_data["updated_by"] = user_id
            
            self._save_guilds(guilds)
            
            logger.info(f"Updated settings for guild {guild_id}")
            
            return {
                "success": True,
                "message": "Guild settings updated successfully",
                "guild_id": guild_id,
                "settings": guild_data["settings"]
            }
            
        except Exception as e:
            logger.error(f"Error updating guild settings {guild_id}: {e}")
            return {
                "success": False,
                "message": f"Failed to update guild settings: {str(e)}",
                "guild_id": guild_id
            }
    
    async def _archive_guild_data(self, guild_id: str, guild_data: Dict[str, Any]):
        """Archive guild data when deregistered"""
        try:
            archive_dir = self.data_dir / 'archived'
            archive_dir.mkdir(exist_ok=True)
            
            archive_file = archive_dir / f'guild_{guild_id}.json'
            
            with open(archive_file, 'w') as f:
                json.dump(guild_data, f, indent=2)
            
            logger.info(f"Archived guild data for {guild_id}")
            
        except Exception as e:
            logger.error(f"Error archiving guild data {guild_id}: {e}")
    
    async def get_guild_stats(self) -> Dict[str, Any]:
        """Get statistics about registered guilds"""
        try:
            guilds = self._load_guilds()
            
            stats = {
                "total_guilds": len(guilds),
                "active_guilds": sum(1 for g in guilds.values() if g.get("status") == "active"),
                "guilds_by_status": {},
                "settings_summary": {
                    "auto_reminders_enabled": 0,
                    "vibe_check_enabled": 0,
                    "canvas_enabled": 0,
                    "photo_collection_enabled": 0
                }
            }
            
            # Count by status
            for guild_data in guilds.values():
                status = guild_data.get("status", "unknown")
                stats["guilds_by_status"][status] = stats["guilds_by_status"].get(status, 0) + 1
                
                # Count settings
                settings = guild_data.get("settings", {})
                for setting_key in stats["settings_summary"]:
                    if settings.get(setting_key, False):
                        stats["settings_summary"][setting_key] += 1
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting guild stats: {e}")
            return {
                "success": False,
                "message": f"Failed to get guild stats: {str(e)}"
            }