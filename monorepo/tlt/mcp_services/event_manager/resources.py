from typing import Dict, Any
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.event_manager.service import EventManagerService

# Using loguru logger imported above

def register_resources(mcp: FastMCP, event_manager: EventManagerService):
    """Register MCP resources for the event manager"""
    
    @mcp.resource("events://list")
    def get_events_list() -> str:
        """Get a list of all events with RSVPs"""
        try:
            events = event_manager.list_events()
            
            if not events:
                return "No events found with RSVPs."
            
            result = "Events with RSVPs:\n\n"
            for event_id, stats in events.items():
                result += f"Event ID: {event_id}\n"
                result += f"  Total Responses: {stats['total_responses']}\n"
                result += f"  Emoji Breakdown: {stats['emoji_breakdown']}\n"
                result += f"  Last Updated: {stats['last_updated']}\n\n"
            
            return result
        except Exception as e:
            logger.error(f"Error getting events list: {e}")
            return f"Error retrieving events: {str(e)}"
    
    @mcp.resource("event://{event_id}/summary")
    def get_event_summary(event_id: str) -> str:
        """Get a summary of RSVPs for a specific event"""
        try:
            summary = event_manager.get_event_rsvps(event_id)
            
            result = f"Event RSVP Summary for {event_id}:\n\n"
            result += f"Total Responses: {summary.total_responses}\n"
            result += f"Emoji Breakdown: {summary.emoji_breakdown}\n"
            result += f"Response Rate: {summary.response_rate:.1%}\n"
            result += f"Last Updated: {summary.last_updated}\n\n"
            
            if summary.rsvps:
                result += "Individual RSVPs:\n"
                for rsvp in summary.rsvps:
                    result += f"  User {rsvp.user_id}: {rsvp.emoji} (responded {rsvp.response_time})\n"
            else:
                result += "No RSVPs yet.\n"
            
            return result
        except Exception as e:
            logger.error(f"Error getting event summary: {e}")
            return f"Error retrieving event summary: {str(e)}"
    
    @mcp.resource("event://{event_id}/analytics")
    def get_event_analytics_resource(event_id: str) -> str:
        """Get detailed analytics for a specific event"""
        try:
            analytics = event_manager.get_event_analytics(event_id)
            
            result = f"Event Analytics for {event_id}:\n\n"
            result += f"Total Responses: {analytics.total_responses}\n\n"
            
            if analytics.total_responses > 0:
                result += "Emoji Breakdown:\n"
                for emoji, count in analytics.emoji_breakdown.items():
                    percentage = (count / analytics.total_responses) * 100
                    result += f"  {emoji}: {count} ({percentage:.1f}%)\n"
                
                if analytics.response_timeline:
                    result += f"\nResponse Timeline ({len(analytics.response_timeline)} data points):\n"
                    for entry in analytics.response_timeline[-5:]:  # Show last 5 entries
                        result += f"  {entry['time']}: {entry['count']} responses\n"
                
                if analytics.peak_response_time:
                    result += f"\nPeak Response Time: {analytics.peak_response_time}\n"
                
                if analytics.average_response_time:
                    result += f"Average Response Time: {analytics.average_response_time:.1f} hours\n"
            else:
                result += "No responses to analyze yet.\n"
            
            return result
        except Exception as e:
            logger.error(f"Error getting event analytics: {e}")
            return f"Error retrieving event analytics: {str(e)}"
    
    @mcp.resource("user://{user_id}/rsvps")
    def get_user_rsvps_resource(user_id: str) -> str:
        """Get all RSVPs for a specific user"""
        try:
            rsvps = event_manager.get_user_rsvps(user_id)
            
            if not rsvps:
                return f"User {user_id} has no RSVPs."
            
            result = f"RSVPs for User {user_id}:\n\n"
            result += f"Total RSVPs: {len(rsvps)}\n\n"
            
            # Group by emoji
            by_emoji = {}
            for rsvp in rsvps:
                emoji = rsvp.emoji
                if emoji not in by_emoji:
                    by_emoji[emoji] = []
                by_emoji[emoji].append(rsvp)
            
            for emoji, emoji_rsvps in by_emoji.items():
                result += f"{emoji} ({len(emoji_rsvps)}):\n"
                for rsvp in emoji_rsvps:
                    result += f"  Event {rsvp.event_id} - responded {rsvp.response_time}\n"
                result += "\n"
            
            return result
        except Exception as e:
            logger.error(f"Error getting user RSVPs: {e}")
            return f"Error retrieving user RSVPs: {str(e)}"
    
    @mcp.resource("rsvp://{rsvp_id}")
    def get_rsvp_details(rsvp_id: str) -> str:
        """Get detailed information about a specific RSVP"""
        try:
            rsvp = event_manager.get_rsvp(rsvp_id)
            
            result = f"RSVP Details for {rsvp_id}:\n\n"
            result += f"Event ID: {rsvp.event_id}\n"
            result += f"User ID: {rsvp.user_id}\n"
            result += f"Emoji: {rsvp.emoji}\n"
            result += f"Response Time: {rsvp.response_time}\n"
            result += f"Created: {rsvp.created_at}\n"
            result += f"Last Updated: {rsvp.updated_at}\n"
            
            if rsvp.metadata:
                result += f"\nMetadata:\n"
                for key, value in rsvp.metadata.items():
                    result += f"  {key}: {value}\n"
            
            return result
        except ValueError as e:
            return f"RSVP not found: {str(e)}"
        except Exception as e:
            logger.error(f"Error getting RSVP details: {e}")
            return f"Error retrieving RSVP details: {str(e)}"
    
    @mcp.resource("stats://server")
    def get_server_stats() -> str:
        """Get overall server statistics"""
        try:
            total_rsvps = len(event_manager.rsvps)
            total_events = len(event_manager.event_rsvps)
            
            result = "Event Manager Server Statistics:\n\n"
            result += f"Total RSVPs: {total_rsvps}\n"
            result += f"Total Events with RSVPs: {total_events}\n"
            
            if total_events > 0:
                avg_rsvps_per_event = total_rsvps / total_events
                result += f"Average RSVPs per Event: {avg_rsvps_per_event:.1f}\n"
            
            # Emoji breakdown across all RSVPs
            if total_rsvps > 0:
                emoji_counts = {}
                for rsvp_data in event_manager.rsvps.values():
                    emoji = rsvp_data['emoji']
                    emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1
                
                result += "\nOverall Emoji Distribution:\n"
                for emoji, count in emoji_counts.items():
                    percentage = (count / total_rsvps) * 100
                    result += f"  {emoji}: {count} ({percentage:.1f}%)\n"
            
            return result
        except Exception as e:
            logger.error(f"Error getting server stats: {e}")
            return f"Error retrieving server statistics: {str(e)}"