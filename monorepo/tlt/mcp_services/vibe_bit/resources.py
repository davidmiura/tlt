from typing import Dict, Any
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.vibe_bit.service import VibeBitService
from tlt.mcp_services.vibe_bit.canvas_renderer import CanvasRenderer
from tlt.mcp_services.vibe_bit.models import ElementType

# Using loguru logger imported above

def register_resources(mcp: FastMCP, service: VibeBitService, renderer: CanvasRenderer):
    """Register MCP resources for the vibe bit service"""
    
    @mcp.resource("vibe://canvas/{event_id}")
    def get_vibe_canvas_info(event_id: str) -> str:
        """Get vibe canvas configuration and status for an event"""
        try:
            config = service.get_canvas_config(event_id)
            
            if not config:
                return f"No vibe canvas found for event {event_id}."
            
            result = f"Vibe Canvas for Event {event_id}:\n\n"
            result += f"Canvas ID: {config.canvas_id}\n"
            result += f"Status: {'✅ ACTIVE' if config.activated else '❌ INACTIVE'}\n"
            result += f"Dimensions: {config.width}x{config.height} pixels\n"
            result += f"Grid Size: {config.grid_size}px cells\n"
            result += f"Background: {config.background_color}\n"
            result += f"Overlap Allowed: {'✅ YES' if config.allow_overlap else '❌ NO'}\n"
            result += f"Rate Limit: {config.rate_limit_hours} hour(s) between placements\n"
            result += f"Placement Window: {config.max_hours_after_event} hours after event start\n"
            
            if config.event_start_time:
                result += f"Event Start Time: {config.event_start_time}\n"
                
                # Calculate time window
                from datetime import timedelta
                end_time = config.event_start_time + timedelta(hours=config.max_hours_after_event)
                result += f"Placement Deadline: {end_time}\n"
                
                # Check if currently accepting
                accepting = service.check_time_window(event_id)
                result += f"Currently Accepting: {'✅ YES' if accepting else '❌ NO'}\n"
            else:
                result += "Event Start Time: Not set\n"
                result += "Currently Accepting: Based on activation status only\n"
            
            result += f"Admin: {config.admin_user_id}\n"
            result += f"Created: {config.created_at}\n"
            result += f"Last Updated: {config.updated_at}\n"
            
            # Add element statistics
            elements = service.get_canvas_elements(event_id)
            result += f"\nCurrent Elements: {len(elements)}\n"
            
            if elements:
                emoji_count = len([e for e in elements if e.element_type == ElementType.EMOJI])
                color_count = len([e for e in elements if e.element_type == ElementType.COLOR_BLOCK])
                unique_users = len(set(e.user_id for e in elements))
                
                result += f"  Emojis: {emoji_count}\n"
                result += f"  Color Blocks: {color_count}\n"
                result += f"  Unique Contributors: {unique_users}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting vibe canvas info: {e}")
            return f"Error retrieving vibe canvas information: {str(e)}"
    
    @mcp.resource("vibe://elements/{event_id}")
    def get_vibe_elements_list(event_id: str) -> str:
        """Get all elements placed on the vibe canvas"""
        try:
            config = service.get_canvas_config(event_id)
            if not config:
                return f"No vibe canvas found for event {event_id}."
            
            elements = service.get_canvas_elements(event_id)
            
            if not elements:
                return f"No elements placed on vibe canvas for event {event_id}."
            
            result = f"Vibe Elements for Event {event_id}:\n\n"
            result += f"Total Elements: {len(elements)}\n"
            result += f"Canvas Size: {config.width}x{config.height}\n\n"
            
            # Group by type
            emoji_elements = [e for e in elements if e.element_type == ElementType.EMOJI]
            color_elements = [e for e in elements if e.element_type == ElementType.COLOR_BLOCK]
            
            if emoji_elements:
                result += f"🎭 Emojis ({len(emoji_elements)}):\n"
                for element in sorted(emoji_elements, key=lambda x: x.placed_at, reverse=True)[:10]:
                    result += f"  {element.content} at ({element.position[0]}, {element.position[1]}) by {element.user_id}\n"
                    result += f"    Placed: {element.placed_at}\n"
                if len(emoji_elements) > 10:
                    result += f"  ... and {len(emoji_elements) - 10} more\n"
                result += "\n"
            
            if color_elements:
                result += f"🎨 Color Blocks ({len(color_elements)}):\n"
                for element in sorted(color_elements, key=lambda x: x.placed_at, reverse=True)[:10]:
                    result += f"  {element.content} at ({element.position[0]}, {element.position[1]}) by {element.user_id}\n"
                    result += f"    Placed: {element.placed_at}\n"
                if len(color_elements) > 10:
                    result += f"  ... and {len(color_elements) - 10} more\n"
                result += "\n"
            
            # Activity summary
            user_counts = {}
            for element in elements:
                user_counts[element.user_id] = user_counts.get(element.user_id, 0) + 1
            
            result += "👥 Most Active Contributors:\n"
            sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)
            for user_id, count in sorted_users[:5]:
                result += f"  {user_id}: {count} elements\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting vibe elements: {e}")
            return f"Error retrieving vibe elements: {str(e)}"
    
    @mcp.resource("vibe://stats/{event_id}")
    def get_vibe_canvas_stats(event_id: str) -> str:
        """Get detailed statistics for the vibe canvas"""
        try:
            stats = service.get_canvas_stats(event_id)
            
            if not stats:
                return f"No vibe canvas statistics found for event {event_id}."
            
            result = f"Vibe Canvas Statistics for Event {event_id}:\n\n"
            result += f"📊 Overall Stats:\n"
            result += f"  Total Elements: {stats.total_elements}\n"
            result += f"  Unique Contributors: {stats.unique_users}\n"
            result += f"  Canvas Coverage: {stats.coverage_percentage:.1f}%\n\n"
            
            result += f"🎯 Element Breakdown:\n"
            emoji_count = stats.elements_by_type.get(ElementType.EMOJI, 0)
            color_count = stats.elements_by_type.get(ElementType.COLOR_BLOCK, 0)
            result += f"  Emojis: {emoji_count}\n"
            result += f"  Color Blocks: {color_count}\n\n"
            
            if stats.most_active_user:
                result += f"🏆 Top Contributor: {stats.most_active_user}\n"
            
            if stats.most_used_emoji:
                result += f"🎭 Most Used Emoji: {stats.most_used_emoji}\n"
            
            if stats.most_used_color:
                result += f"🎨 Most Used Color: {stats.most_used_color}\n"
            
            if stats.placement_timeline:
                result += f"\n📈 Activity Timeline:\n"
                for entry in stats.placement_timeline[-5:]:  # Show last 5 time periods
                    result += f"  {entry['time']}: {entry['count']} placements\n"
            
            result += f"\nLast Updated: {stats.last_updated}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting vibe canvas stats: {e}")
            return f"Error retrieving canvas statistics: {str(e)}"
    
    @mcp.resource("vibe://user/{user_id}")
    def get_user_vibe_history(user_id: str) -> str:
        """Get vibe placement history for a user"""
        try:
            elements = service.get_user_elements(user_id)
            
            if not elements:
                return f"No vibe placements found for user {user_id}."
            
            result = f"Vibe Placement History for User {user_id}:\n\n"
            result += f"Total Placements: {len(elements)}\n\n"
            
            # Group by event
            by_event = {}
            for element in elements:
                event_id = element.event_id
                if event_id not in by_event:
                    by_event[event_id] = []
                by_event[event_id].append(element)
            
            for event_id, event_elements in by_event.items():
                result += f"Event {event_id} ({len(event_elements)} placements):\n"
                
                emoji_count = len([e for e in event_elements if e.element_type == ElementType.EMOJI])
                color_count = len([e for e in event_elements if e.element_type == ElementType.COLOR_BLOCK])
                
                result += f"  Emojis: {emoji_count}, Color Blocks: {color_count}\n"
                
                # Show recent placements
                for element in sorted(event_elements, key=lambda x: x.placed_at, reverse=True)[:3]:
                    type_icon = "🎭" if element.element_type == ElementType.EMOJI else "🎨"
                    result += f"  {type_icon} {element.content} at ({element.position[0]}, {element.position[1]})\n"
                    result += f"    {element.placed_at}\n"
                
                if len(event_elements) > 3:
                    result += f"  ... and {len(event_elements) - 3} more\n"
                
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user vibe history: {e}")
            return f"Error retrieving user vibe history: {str(e)}"
    
    @mcp.resource("vibe://progress/{event_id}")
    def get_vibe_canvas_progress(event_id: str) -> str:
        """Get real-time progress of the vibe canvas"""
        try:
            config = service.get_canvas_config(event_id)
            if not config:
                return f"No vibe canvas found for event {event_id}."
            
            elements = service.get_canvas_elements(event_id)
            
            result = f"Vibe Canvas Progress for Event {event_id}:\n\n"
            
            if not config.activated:
                result += "❌ Canvas is currently INACTIVE\n\n"
            elif not service.check_time_window(event_id):
                result += "⏰ Canvas placement window is CLOSED\n\n"
            else:
                result += "✅ Canvas is ACTIVE and accepting placements\n\n"
            
            # Calculate grid utilization
            total_grid_cells = (config.width // config.grid_size) * (config.height // config.grid_size)
            filled_cells = len(elements)
            utilization = (filled_cells / total_grid_cells) * 100 if total_grid_cells > 0 else 0
            
            result += f"📏 Canvas: {config.width}x{config.height} ({total_grid_cells} grid cells)\n"
            result += f"🎯 Utilization: {filled_cells}/{total_grid_cells} cells ({utilization:.1f}%)\n"
            result += f"📊 Progress Bar: {'█' * int(utilization / 5)}{'░' * (20 - int(utilization / 5))} {utilization:.1f}%\n\n"
            
            if elements:
                # Recent activity
                recent_elements = sorted(elements, key=lambda x: x.placed_at, reverse=True)[:5]
                result += "🕒 Recent Activity:\n"
                for element in recent_elements:
                    type_icon = "🎭" if element.element_type == ElementType.EMOJI else "🎨"
                    time_diff = service._calculate_time_ago(element.placed_at)
                    result += f"  {type_icon} {element.content} by {element.user_id} - {time_diff}\n"
                
                # Activity over time
                if len(elements) > 1:
                    first_placement = min(elements, key=lambda x: x.placed_at).placed_at
                    last_placement = max(elements, key=lambda x: x.placed_at).placed_at
                    duration = last_placement - first_placement
                    
                    result += f"\n⏱️ Activity Span: {duration.total_seconds() / 3600:.1f} hours\n"
                    result += f"📈 Average Rate: {len(elements) / max(1, duration.total_seconds() / 3600):.1f} placements/hour\n"
            else:
                result += "🔍 No elements placed yet. Be the first to add your vibe!\n"
            
            # Time window info
            if config.event_start_time:
                from datetime import datetime, timedelta, timezone
                now = datetime.now(timezone.utc)
                
                if now < config.event_start_time:
                    time_until_start = config.event_start_time - now
                    result += f"\n⏳ Event starts in: {time_until_start.total_seconds() / 3600:.1f} hours\n"
                else:
                    end_time = config.event_start_time + timedelta(hours=config.max_hours_after_event)
                    if now < end_time:
                        time_remaining = end_time - now
                        result += f"\n⏳ Time remaining: {time_remaining.total_seconds() / 3600:.1f} hours\n"
                    else:
                        result += f"\n🏁 Placement window has ended\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting vibe canvas progress: {e}")
            return f"Error retrieving canvas progress: {str(e)}"
    
    @mcp.resource("vibe://palettes/colors")
    def get_color_palettes_resource() -> str:
        """Get available color palettes for vibe bit placement"""
        try:
            palettes = service.get_color_palettes()
            
            result = "🎨 Available Color Palettes:\n\n"
            
            for palette in palettes:
                result += f"**{palette['name'].title()}**\n"
                result += f"  Description: {palette['description']}\n"
                result += f"  Colors: "
                
                # Show color codes
                color_display = []
                for color in palette['colors']:
                    color_display.append(f"{color}")
                
                result += " ".join(color_display)
                result += f" ({len(palette['colors'])} colors)\n\n"
            
            result += "💡 Usage: Use any hex color code like #FF0000 for red\n"
            result += "🎯 Tip: Choose colors that contrast well with the background\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting color palettes: {e}")
            return f"Error retrieving color palettes: {str(e)}"
    
    @mcp.resource("vibe://emojis/sets")
    def get_emoji_sets_resource() -> str:
        """Get available emoji sets for vibe bit placement"""
        try:
            from tlt.mcp_services.vibe_bit.models import EMOJI_SETS
            
            result = "🎭 Available Emoji Sets:\n\n"
            
            for set_name, emojis in EMOJI_SETS.items():
                result += f"**{set_name.title()}**\n"
                result += f"  Emojis: {''.join(emojis[:10])}"
                if len(emojis) > 10:
                    result += f" (+{len(emojis) - 10} more)"
                result += f" ({len(emojis)} total)\n\n"
            
            result += "💡 Usage: Copy any emoji and use it as content\n"
            result += "🎯 Tip: Mix different emoji types for a vibrant canvas\n"
            result += "⚠️ Note: Some emojis may render differently on different devices\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting emoji sets: {e}")
            return f"Error retrieving emoji sets: {str(e)}"
    
    @mcp.resource("vibe://server/stats")
    def get_vibe_server_stats() -> str:
        """Get overall vibe bit server statistics"""
        try:
            total_canvases = len(service.canvas_configs)
            total_elements = sum(len(elements) for elements in service.vibe_elements.values())
            active_canvases = len([config for config in service.canvas_configs.values() if config.activated])
            
            result = "Vibe Bit Server Statistics:\n\n"
            result += f"📊 Overall Stats:\n"
            result += f"  Total Canvases: {total_canvases}\n"
            result += f"  Active Canvases: {active_canvases}\n"
            result += f"  Total Elements Placed: {total_elements}\n\n"
            
            if total_elements > 0:
                # Element type breakdown across all canvases
                total_emojis = 0
                total_colors = 0
                all_users = set()
                
                for elements in service.vibe_elements.values():
                    for element in elements:
                        all_users.add(element.user_id)
                        if element.element_type == ElementType.EMOJI:
                            total_emojis += 1
                        else:
                            total_colors += 1
                
                result += f"🎭 Element Breakdown:\n"
                result += f"  Total Emojis: {total_emojis}\n"
                result += f"  Total Color Blocks: {total_colors}\n"
                result += f"  Unique Users: {len(all_users)}\n\n"
                
                # Active canvas info
                if active_canvases > 0:
                    result += f"✅ Active Canvases:\n"
                    for event_id, config in service.canvas_configs.items():
                        if config.activated:
                            elements_count = len(service.vibe_elements.get(event_id, []))
                            accepting = service.check_time_window(event_id)
                            status = "🟢 Accepting" if accepting else "🔴 Closed"
                            result += f"  Event {event_id}: {elements_count} elements ({status})\n"
                    result += "\n"
            
            if total_canvases > active_canvases:
                inactive_count = total_canvases - active_canvases
                result += f"💤 Inactive Canvases: {inactive_count}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting vibe server stats: {e}")
            return f"Error retrieving server statistics: {str(e)}"


# Helper function for time calculation (add to service if needed)
def _calculate_time_ago(placed_at):
    """Calculate human-readable time ago"""
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc)
    diff = now - placed_at
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"

# Add the helper function to the service class
setattr(VibeBitService, '_calculate_time_ago', lambda self, placed_at: _calculate_time_ago(placed_at))