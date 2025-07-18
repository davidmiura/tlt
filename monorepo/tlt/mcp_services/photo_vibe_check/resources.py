from typing import Dict, Any
from loguru import logger
from datetime import timedelta
from fastmcp import FastMCP
from tlt.mcp_services.photo_vibe_check.service import PhotoVibeCheckService
from tlt.mcp_services.photo_vibe_check.models import PhotoStatus

# Using loguru logger imported above

def register_resources(mcp: FastMCP, service: PhotoVibeCheckService):
    """Register MCP resources for the photo vibe check service"""
    
    @mcp.resource("photo://config/{event_id}")
    def get_event_photo_config(event_id: str) -> str:
        """Get photo collection configuration for an event"""
        try:
            config = service.get_event_config(event_id)
            
            if not config:
                return f"No photo collection configuration found for event {event_id}."
            
            result = f"Photo Collection Configuration for Event {event_id}:\n\n"
            result += f"Status: {'✅ ACTIVE' if config.activated else '❌ INACTIVE'}\n"
            result += f"Rate Limit: {config.rate_limit_hours} hour(s) between submissions\n"
            result += f"Submission Window: {config.max_hours_after_event} hours after event start\n"
            
            if config.event_start_time:
                result += f"Event Start Time: {config.event_start_time}\n"
                
                # Calculate time window
                end_time = config.event_start_time + timedelta(hours=config.max_hours_after_event)
                result += f"Submission Deadline: {end_time}\n"
                
                # Check if currently accepting
                accepting = service.check_time_window(event_id)
                result += f"Currently Accepting: {'✅ YES' if accepting else '❌ NO'}\n"
            else:
                result += "Event Start Time: Not set\n"
                result += "Currently Accepting: Based on activation status only\n"
            
            result += f"Pre-event Photos: {len(config.pre_event_photos)} uploaded\n"
            result += f"Admin: {config.admin_user_id}\n"
            result += f"Created: {config.created_at}\n"
            result += f"Last Updated: {config.updated_at}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting event photo config: {e}")
            return f"Error retrieving photo configuration: {str(e)}"
    
    @mcp.resource("photo://submissions/{event_id}")
    def get_event_photo_submissions(event_id: str) -> str:
        """Get all photo submissions for an event"""
        try:
            submissions = service.get_event_submissions(event_id)
            
            if not submissions:
                return f"No photo submissions found for event {event_id}."
            
            result = f"Photo Submissions for Event {event_id}:\n\n"
            result += f"Total Submissions: {len(submissions)}\n\n"
            
            # Group by status
            by_status = {}
            for submission in submissions:
                status = submission.status
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(submission)
            
            # Show breakdown by status
            for status in PhotoStatus:
                count = len(by_status.get(status, []))
                status_icon = {
                    PhotoStatus.SUBMITTED: "📤",
                    PhotoStatus.PROCESSING: "⚙️",
                    PhotoStatus.APPROVED: "✅",
                    PhotoStatus.REJECTED: "❌",
                    PhotoStatus.CURATED: "🎨"
                }.get(status, "📋")
                
                result += f"{status_icon} {status.value.replace('_', ' ').title()}: {count}\n"
            
            result += "\nRecent Submissions:\n"
            
            # Show latest 10 submissions
            recent_submissions = sorted(submissions, key=lambda x: x.submitted_at, reverse=True)[:10]
            
            for submission in recent_submissions:
                status_icon = {
                    PhotoStatus.SUBMITTED: "📤",
                    PhotoStatus.PROCESSING: "⚙️", 
                    PhotoStatus.APPROVED: "✅",
                    PhotoStatus.REJECTED: "❌",
                    PhotoStatus.CURATED: "🎨"
                }.get(submission.status, "📋")
                
                result += f"\n{status_icon} Photo {submission.photo_id[:8]}...\n"
                result += f"  User: {submission.user_id}\n"
                result += f"  Status: {submission.status.value}\n"
                result += f"  Submitted: {submission.submitted_at}\n"
                
                # Include analysis if available
                analysis = service.get_photo_analysis(submission.photo_id)
                if analysis:
                    result += f"  Score: {analysis.overall_score:.2f}/1.0\n"
                    result += f"  Quality: {analysis.quality_rating.value}\n"
                    result += f"  Relevance: {analysis.relevance_rating.value}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting event photo submissions: {e}")
            return f"Error retrieving photo submissions: {str(e)}"
    
    @mcp.resource("photo://analysis/{photo_id}")
    def get_photo_analysis_details(photo_id: str) -> str:
        """Get detailed analysis for a specific photo"""
        try:
            submission = service.get_photo_submission(photo_id)
            if not submission:
                return f"Photo submission {photo_id} not found."
            
            analysis = service.get_photo_analysis(photo_id)
            processing_state = service.get_processing_state(photo_id)
            
            result = f"Photo Analysis for {photo_id}:\n\n"
            result += f"Event: {submission.event_id}\n"
            result += f"User: {submission.user_id}\n"
            result += f"Submitted: {submission.submitted_at}\n"
            result += f"Status: {submission.status.value}\n\n"
            
            if processing_state:
                result += "Processing Status:\n"
                result += f"  Current Step: {processing_state.current_step}\n"
                result += f"  Progress: {processing_state.progress:.1%}\n"
                if processing_state.error:
                    result += f"  Error: {processing_state.error}\n"
                result += f"  Updated: {processing_state.updated_at}\n\n"
            
            if analysis:
                result += "Analysis Results:\n"
                result += f"  Overall Score: {analysis.overall_score:.2f}/1.0\n\n"
                
                result += "Quality Assessment:\n"
                result += f"  Score: {analysis.quality_score:.2f}/1.0\n"
                result += f"  Rating: {analysis.quality_rating.value.replace('_', ' ').title()}\n"
                result += f"  Size Check: {'✅ PASS' if analysis.size_check else '❌ FAIL'}\n\n"
                
                result += "Relevance Assessment:\n"
                result += f"  Score: {analysis.relevance_score:.2f}/1.0\n"
                result += f"  Rating: {analysis.relevance_rating.value.replace('_', ' ').title()}\n\n"
                
                if analysis.similarity_scores:
                    result += "Similarity to Pre-event Photos:\n"
                    for ref_photo, score in analysis.similarity_scores.items():
                        result += f"  {ref_photo}: {score:.2f}/1.0\n"
                    result += "\n"
                
                result += "Content Analysis:\n"
                result += f"  {analysis.content_analysis}\n\n"
                
                result += "Reasoning:\n"
                result += f"  {analysis.reasoning}\n\n"
                
                result += f"Analyzed: {analysis.analyzed_at}\n"
            else:
                result += "Analysis: Not yet completed or failed\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting photo analysis: {e}")
            return f"Error retrieving photo analysis: {str(e)}"
    
    @mcp.resource("photo://user/{user_id}")
    def get_user_photo_history(user_id: str) -> str:
        """Get photo submission history for a user"""
        try:
            submissions = service.get_user_submissions(user_id)
            
            if not submissions:
                return f"No photo submissions found for user {user_id}."
            
            result = f"Photo Submission History for User {user_id}:\n\n"
            result += f"Total Submissions: {len(submissions)}\n\n"
            
            # Group by event
            by_event = {}
            for submission in submissions:
                event_id = submission.event_id
                if event_id not in by_event:
                    by_event[event_id] = []
                by_event[event_id].append(submission)
            
            for event_id, event_submissions in by_event.items():
                result += f"Event {event_id} ({len(event_submissions)} submissions):\n"
                
                for submission in sorted(event_submissions, key=lambda x: x.submitted_at, reverse=True):
                    status_icon = {
                        PhotoStatus.SUBMITTED: "📤",
                        PhotoStatus.PROCESSING: "⚙️",
                        PhotoStatus.APPROVED: "✅", 
                        PhotoStatus.REJECTED: "❌",
                        PhotoStatus.CURATED: "🎨"
                    }.get(submission.status, "📋")
                    
                    result += f"  {status_icon} {submission.photo_id[:8]}... - {submission.status.value}\n"
                    result += f"    Submitted: {submission.submitted_at}\n"
                    
                    analysis = service.get_photo_analysis(submission.photo_id)
                    if analysis:
                        result += f"    Score: {analysis.overall_score:.2f}/1.0\n"
                    
                result += "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user photo history: {e}")
            return f"Error retrieving user photo history: {str(e)}"
    
    @mcp.resource("photo://slideshow/{event_id}")
    def get_event_slideshow(event_id: str) -> str:
        """Get slideshow information for an event"""
        try:
            slideshow = service.get_event_slideshow(event_id)
            
            if not slideshow:
                return f"No slideshow found for event {event_id}. Generate one using the generate_event_slideshow tool."
            
            result = f"Slideshow for Event {event_id}:\n\n"
            result += f"Slideshow ID: {slideshow.slideshow_id}\n"
            result += f"Created: {slideshow.created_at}\n"
            result += f"Total Original Submissions: {slideshow.total_submissions}\n"
            result += f"Accepted for Slideshow: {slideshow.accepted_count}\n"
            result += f"Rejected: {slideshow.rejected_count}\n"
            result += f"Photos in Slideshow: {len(slideshow.photos)}\n\n"
            
            if slideshow.photos:
                result += "Photos (ranked by score):\n\n"
                
                for i, photo in enumerate(slideshow.photos, 1):
                    result += f"{i}. Photo {photo.photo_id[:8]}... (Score: {photo.score:.2f})\n"
                    result += f"   User: {photo.user_id}\n"
                    result += f"   Submitted: {photo.submitted_at}\n"
                    result += f"   URL: {photo.photo_url}\n"
                    if photo.caption:
                        result += f"   Caption: {photo.caption}\n"
                    result += "\n"
            else:
                result += "No photos in slideshow.\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting event slideshow: {e}")
            return f"Error retrieving event slideshow: {str(e)}"
    
    @mcp.resource("photo://stats/server")
    def get_photo_server_stats() -> str:
        """Get overall photo server statistics"""
        try:
            total_submissions = len(service.photo_submissions)
            total_events = len(service.event_configs)
            total_slideshows = len(service.slideshows)
            
            result = "Photo Vibe Check Server Statistics:\n\n"
            result += f"Total Photo Submissions: {total_submissions}\n"
            result += f"Total Events Configured: {total_events}\n"
            result += f"Total Slideshows Created: {total_slideshows}\n\n"
            
            if total_submissions > 0:
                # Status breakdown
                status_counts = {}
                for submission in service.photo_submissions.values():
                    status = submission.status
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                result += "Submission Status Breakdown:\n"
                for status in PhotoStatus:
                    count = status_counts.get(status, 0)
                    percentage = (count / total_submissions) * 100
                    result += f"  {status.value.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n"
                
                # Analysis statistics
                analyses = service.photo_analyses
                if analyses:
                    avg_quality = sum(a.quality_score for a in analyses.values()) / len(analyses)
                    avg_relevance = sum(a.relevance_score for a in analyses.values()) / len(analyses)
                    avg_overall = sum(a.overall_score for a in analyses.values()) / len(analyses)
                    
                    result += f"\nAnalysis Averages:\n"
                    result += f"  Quality Score: {avg_quality:.2f}/1.0\n"
                    result += f"  Relevance Score: {avg_relevance:.2f}/1.0\n"
                    result += f"  Overall Score: {avg_overall:.2f}/1.0\n"
            
            # Active events
            active_events = [config for config in service.event_configs.values() if config.activated]
            result += f"\nActive Events: {len(active_events)}\n"
            
            for config in active_events:
                accepting = service.check_time_window(config.event_id)
                result += f"  Event {config.event_id}: {'✅ Accepting' if accepting else '❌ Closed'}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting photo server stats: {e}")
            return f"Error retrieving server statistics: {str(e)}"