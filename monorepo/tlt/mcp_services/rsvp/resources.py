from typing import Dict, Any
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.rsvp.service import RSVPService

# Using loguru logger imported above

def register_resources(mcp: FastMCP, rsvp_service: RSVPService):
    """Register MCP resources for the RSVP service"""
    
    @mcp.resource("rsvp://event/{event_id}")
    def get_event_rsvps_resource(event_id: str) -> str:
        """Get RSVP information for a specific event"""
        try:
            summary = rsvp_service.get_event_rsvps(event_id)
            
            result = f"RSVP Summary for Event {event_id}\n"
            result += "=" * (len(event_id) + 25) + "\n\n"
            
            result += f"📊 Overview:\n"
            result += f"  Total Responses: {summary.total_responses}\n"
            result += f"  Response Rate: {summary.response_rate:.1%}\n"
            result += f"  Last Updated: {summary.last_updated}\n\n"
            
            if summary.emoji_breakdown:
                result += f"😀 Emoji Breakdown:\n"
                sorted_emojis = sorted(summary.emoji_breakdown.items(), key=lambda x: x[1], reverse=True)
                for emoji, count in sorted_emojis:
                    percentage = (count / summary.total_responses) * 100 if summary.total_responses > 0 else 0
                    result += f"  {emoji}: {count} ({percentage:.1f}%)\n"
                result += "\n"
            
            if summary.rsvps:
                result += f"👥 Recent RSVPs (last 10):\n"
                recent_rsvps = sorted(summary.rsvps, key=lambda x: x.response_time, reverse=True)[:10]
                for rsvp in recent_rsvps:
                    result += f"  {rsvp.emoji} {rsvp.user_id} - {rsvp.response_time.strftime('%Y-%m-%d %H:%M')}\n"
                
                if len(summary.rsvps) > 10:
                    result += f"  ... and {len(summary.rsvps) - 10} more\n"
            else:
                result += "No RSVPs yet for this event.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting event RSVPs resource: {e}")
            return f"Error retrieving RSVP information for event {event_id}: {str(e)}"
    
    @mcp.resource("rsvp://user/{user_id}")
    def get_user_rsvps_resource(user_id: str) -> str:
        """Get RSVP information for a specific user"""
        try:
            summary = rsvp_service.get_user_rsvps(user_id)
            
            result = f"RSVP History for User {user_id}\n"
            result += "=" * (len(user_id) + 20) + "\n\n"
            
            result += f"📊 Overview:\n"
            result += f"  Total RSVPs: {summary.total_rsvps}\n"
            result += f"  Last Updated: {summary.last_updated}\n\n"
            
            if summary.events_by_emoji:
                result += f"😀 Events by Emoji:\n"
                for emoji, event_ids in summary.events_by_emoji.items():
                    result += f"  {emoji}: {len(event_ids)} event(s)\n"
                    for event_id in event_ids[:3]:  # Show first 3 events
                        result += f"    • {event_id}\n"
                    if len(event_ids) > 3:
                        result += f"    ... and {len(event_ids) - 3} more\n"
                result += "\n"
            
            if summary.recent_rsvps:
                result += f"📅 Recent RSVPs:\n"
                for rsvp in summary.recent_rsvps:
                    result += f"  {rsvp.emoji} Event {rsvp.event_id} - {rsvp.response_time.strftime('%Y-%m-%d %H:%M')}\n"
            else:
                result += "No RSVPs found for this user.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user RSVPs resource: {e}")
            return f"Error retrieving RSVP information for user {user_id}: {str(e)}"
    
    @mcp.resource("rsvp://analytics/{event_id}")
    def get_rsvp_analytics_resource(event_id: str) -> str:
        """Get detailed RSVP analytics for an event"""
        try:
            analytics = rsvp_service.get_rsvp_analytics(event_id)
            
            result = f"RSVP Analytics for Event {event_id}\n"
            result += "=" * (len(event_id) + 25) + "\n\n"
            
            result += f"📈 Statistics:\n"
            result += f"  Total Responses: {analytics.total_responses}\n"
            result += f"  Unique Users: {analytics.unique_users}\n"
            
            if analytics.most_popular_emoji:
                result += f"  Most Popular Emoji: {analytics.most_popular_emoji}\n"
            
            if analytics.peak_response_time:
                result += f"  Peak Response Time: {analytics.peak_response_time}\n"
            
            if analytics.average_response_time is not None:
                result += f"  Average Response Time: {analytics.average_response_time:.1f} hours\n"
            
            result += "\n"
            
            if analytics.emoji_breakdown:
                result += f"😀 Emoji Distribution:\n"
                total = analytics.total_responses
                sorted_emojis = sorted(analytics.emoji_breakdown.items(), key=lambda x: x[1], reverse=True)
                for emoji, count in sorted_emojis:
                    percentage = (count / total) * 100 if total > 0 else 0
                    bar_length = int(percentage / 5)  # Scale for visual bar
                    bar = "█" * bar_length + "░" * (20 - bar_length)
                    result += f"  {emoji} {bar} {count} ({percentage:.1f}%)\n"
                result += "\n"
            
            if analytics.response_timeline:
                result += f"📊 Response Timeline:\n"
                result += "  Recent activity periods:\n"
                for entry in analytics.response_timeline[-10:]:  # Show last 10 periods
                    result += f"    {entry['time']}: {entry['count']} responses\n"
                
                if len(analytics.response_timeline) > 10:
                    result += f"    ... and {len(analytics.response_timeline) - 10} earlier periods\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting RSVP analytics resource: {e}")
            return f"Error retrieving RSVP analytics for event {event_id}: {str(e)}"
    
    @mcp.resource("rsvp://stats")
    def get_rsvp_stats_resource() -> str:
        """Get overall RSVP service statistics"""
        try:
            stats = rsvp_service.get_rsvp_stats()
            
            result = "RSVP Service Statistics\n"
            result += "=" * 25 + "\n\n"
            
            result += f"📊 Overall Stats:\n"
            result += f"  Total RSVPs: {stats['total_rsvps']}\n"
            result += f"  Events with RSVPs: {stats['total_events_with_rsvps']}\n"
            result += f"  Users with RSVPs: {stats['total_users_with_rsvps']}\n"
            result += f"  Avg RSVPs per Event: {stats['average_rsvps_per_event']:.1f}\n"
            result += f"  Avg RSVPs per User: {stats['average_rsvps_per_user']:.1f}\n\n"
            
            if stats['global_emoji_usage']:
                result += f"😀 Global Emoji Usage:\n"
                sorted_emojis = sorted(stats['global_emoji_usage'].items(), key=lambda x: x[1], reverse=True)
                for emoji, count in sorted_emojis[:10]:  # Show top 10
                    percentage = (count / stats['total_rsvps']) * 100 if stats['total_rsvps'] > 0 else 0
                    result += f"  {emoji}: {count} ({percentage:.1f}%)\n"
                
                if len(sorted_emojis) > 10:
                    result += f"  ... and {len(sorted_emojis) - 10} other emojis\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting RSVP stats resource: {e}")
            return f"Error retrieving RSVP service statistics: {str(e)}"
    
    @mcp.resource("rsvp://events")
    def get_events_with_rsvps_resource() -> str:
        """Get list of all events with RSVPs"""
        try:
            events = rsvp_service.list_events_with_rsvps()
            
            result = "Events with RSVPs\n"
            result += "=" * 18 + "\n\n"
            
            if events:
                result += f"📅 Events ({len(events)} total):\n\n"
                
                for event_id in events:
                    summary = rsvp_service.get_event_rsvps(event_id)
                    result += f"  Event: {event_id}\n"
                    result += f"    RSVPs: {summary.total_responses}\n"
                    
                    if summary.emoji_breakdown:
                        top_emoji = max(summary.emoji_breakdown.items(), key=lambda x: x[1])
                        result += f"    Top Emoji: {top_emoji[0]} ({top_emoji[1]} uses)\n"
                    
                    result += f"    Last Updated: {summary.last_updated.strftime('%Y-%m-%d %H:%M')}\n\n"
            else:
                result += "No events with RSVPs found.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting events with RSVPs resource: {e}")
            return f"Error retrieving events with RSVPs: {str(e)}"