"""Guild Manager resources registration"""

from typing import Dict, Any
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.guild_manager.service import GuildManagerService

def register_resources(mcp: FastMCP, service: GuildManagerService):
    """Register all guild manager resources"""
    
    @mcp.resource("guild://list")
    def guild_list() -> str:
        """Resource providing list of all registered guilds"""
        try:
            result = service.list_guilds()
            
            if not result.get("guilds"):
                return "No guilds are currently registered."
            
            guilds = result["guilds"]
            output = f"Registered Guilds ({len(guilds)} total):\n\n"
            
            for guild in guilds:
                status_icon = "✅" if guild.get("status") == "active" else "❌"
                output += f"{status_icon} Guild: {guild.get('guild_name', 'Unknown')}\n"
                output += f"   ID: {guild.get('guild_id')}\n"
                output += f"   Registered: {guild.get('registered_at', 'Unknown')}\n"
                output += f"   Admin: {guild.get('admin_user_name', 'Unknown')}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error retrieving guild list: {str(e)}"
    
    @mcp.resource("guild://stats")
    def guild_stats() -> str:
        """Resource providing guild statistics"""
        try:
            result = service.get_guild_stats()
            
            output = "Guild Manager Statistics:\n\n"
            output += f"Total Registered Guilds: {result.get('total_guilds', 0)}\n"
            output += f"Active Guilds: {result.get('active_guilds', 0)}\n"
            output += f"Inactive Guilds: {result.get('inactive_guilds', 0)}\n"
            output += f"Recently Registered: {result.get('recently_registered', 0)} (last 7 days)\n\n"
            
            if result.get('registration_history'):
                output += "Recent Registration Activity:\n"
                for entry in result['registration_history'][-5:]:
                    action_icon = "➕" if entry.get('action') == 'register' else "➖"
                    output += f"{action_icon} {entry.get('guild_name')} - {entry.get('timestamp')}\n"
            
            return output
            
        except Exception as e:
            return f"Error retrieving guild statistics: {str(e)}"
    
    @mcp.resource("guild://active")
    def active_guilds() -> str:
        """Resource providing list of active guilds"""
        try:
            result = service.list_guilds(status="active")
            
            if not result.get("guilds"):
                return "No active guilds found."
            
            guilds = result["guilds"]
            output = f"Active Guilds ({len(guilds)} total):\n\n"
            
            for guild in guilds:
                output += f"✅ {guild.get('guild_name', 'Unknown')}\n"
                output += f"   ID: {guild.get('guild_id')}\n"
                output += f"   Admin: {guild.get('admin_user_name', 'Unknown')}\n"
                output += f"   Events Channel: {guild.get('events_channel_name', 'Unknown')}\n"
                output += f"   Registered: {guild.get('registered_at', 'Unknown')}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error retrieving active guilds: {str(e)}"
    
    logger.info("Guild Manager resources registered successfully")