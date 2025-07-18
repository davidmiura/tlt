import asyncio
import os
from loguru import logger
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from fastmcp import FastMCP
from tlt.mcp_services.photo_vibe_check.service import PhotoVibeCheckService
from tlt.mcp_services.photo_vibe_check.photo_processor import PhotoProcessor
from tlt.mcp_services.photo_vibe_check.models import (
    PhotoStatus,
    SubmitPhotoDmResult,
    ActivatePhotoCollectionResult,
    DeactivatePhotoCollectionResult,
    UpdatePhotoSettingsResult,
    AddPreEventPhotosResult,
    GetPhotoStatusResult,
    GetEventPhotoSummaryResult,
    GenerateEventSlideshowResult,
    GetUserPhotoHistoryResult
)
from tlt.shared.user_state_manager import UserStateManager
from tlt.shared.event_state_manager import EventStateManager

# Using loguru logger imported above

def register_tools(mcp: FastMCP, service: PhotoVibeCheckService, processor: PhotoProcessor):
    """Register all MCP tools for the photo vibe check service"""
    
    # Initialize state managers
    guild_data_dir = os.getenv('GUILD_DATA_DIR', './guild_data')
    data_dir = os.path.join(guild_data_dir, 'data')
    user_state_manager = UserStateManager(data_dir)
    event_state_manager = EventStateManager(data_dir)
    
    @mcp.tool()
    async def submit_photo_dm(
        guild_id: str,
        event_id: str,
        user_id: str,
        photo_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Submit a photo from a Discord DM for event processing.
        
        This tool accepts photo submissions from Discord users who have RSVP'd
        to an event. Photos are subject to rate limiting and time window validation.
        
        Args:
            event_id: The ID of the event
            user_id: The Discord user ID submitting the photo
            photo_url: URL of the photo to submit
            metadata: Optional metadata (source channel, message ID, etc.)
            
        Returns:
            Dict containing submission result and status
        """
        try:
            logger.info(f"=== submit_photo_dm CALLED ===")
            logger.info(f"Event ID: {event_id}")
            logger.info(f"User ID: {user_id}")
            logger.info(f"Photo URL: {photo_url}")
            logger.info(f"Metadata payload: {metadata}")
            
            # Submit photo to service
            logger.info("Calling service.submit_photo...")
            result = await service.submit_photo(event_id, user_id, photo_url, metadata)
            logger.info(f"Service result: {result}")
            
            if result.success:
                logger.info(f"Photo submission successful: {result.photo_id}")
                
                # Extract guild_id from metadata for vibe check
                # guild_id = metadata.get("guild_id") if metadata else None
                # logger.info(f"Guild ID extracted from metadata: {guild_id}")
                
                # Check if promotional images exist for GenZ vibe check
                if guild_id:
                    logger.info(f"Starting GenZ vibe check for photo {result.photo_id}")
                    logger.info(f"Vibe check parameters: photo_id={result.photo_id}, photo_url={photo_url}, event_id={event_id}, user_id={user_id}, guild_id={guild_id}")
                    
                    # Perform GenZ vibe check against promotional images
                    logger.info("Calling processor.process_genz_vibe_check...")
                    vibe_check_result = await processor.process_genz_vibe_check(
                        photo_id=result.photo_id,
                        photo_url=photo_url,
                        event_id=event_id,
                        user_id=user_id,
                        guild_id=guild_id,
                        metadata=metadata
                    )
                    logger.info(f"Vibe check result: {vibe_check_result}")
                    
                    # Start async photo processing (original functionality)
                    logger.info("Starting async photo processing task...")
                    asyncio.create_task(
                        _process_photo_async(service, processor, result.photo_id)
                    )
                    
                    logger.info(f"Photo submitted with vibe check: {result.photo_id} by {user_id} for event {event_id}")
                    
                    # Return result including vibe check data
                    response = {
                        "success": result.success,
                        "photo_id": result.photo_id,
                        "message": result.message,
                        "rate_limit_remaining": result.rate_limit_remaining,
                        "next_allowed_submission": result.next_allowed_submission.isoformat() if result.next_allowed_submission else None,
                        "vibe_check": vibe_check_result
                    }
                    
                    # Save result to UserStateManager
                    submit_result = SubmitPhotoDmResult(
                        success=result.success,
                        photo_id=result.photo_id,
                        message=result.message,
                        rate_limit_remaining=result.rate_limit_remaining,
                        next_allowed_submission=result.next_allowed_submission.isoformat() if result.next_allowed_submission else None,
                        vibe_check=vibe_check_result,
                        event_id=event_id,
                        user_id=user_id,
                        photo_url=photo_url,
                        metadata=metadata
                    )
                    user_state_manager.add_model_entry(guild_id, event_id, user_id, submit_result)
                    
                    # Update event.json with photo submission data
                    event_state_manager.append_to_array_field(guild_id, event_id, "photo_submissions", {
                        "photo_id": result.photo_id,
                        "user_id": user_id,
                        "submitted_at": datetime.now(timezone.utc).isoformat(),
                        "photo_url": photo_url,
                        "status": "submitted",
                        "vibe_check": vibe_check_result
                    })
                    
                    logger.info(f"Final response with vibe check: {response}")
                    return response
                else:
                    # No guild_id, skip vibe check and do normal processing
                    logger.warning("No guild_id found in metadata, skipping GenZ vibe check")
                    asyncio.create_task(
                        _process_photo_async(service, processor, result.photo_id)
                    )
                    logger.info(f"Photo submitted successfully: {result.photo_id} by {user_id} for event {event_id} (no vibe check - missing guild_id)")
                    
                    response = {
                        "success": result.success,
                        "photo_id": result.photo_id,
                        "message": result.message,
                        "rate_limit_remaining": result.rate_limit_remaining,
                        "next_allowed_submission": result.next_allowed_submission.isoformat() if result.next_allowed_submission else None,
                        "vibe_check": {
                            "success": False,
                            "message": "Vibe check skipped - no guild information",
                            "vibe_score": 0.0,
                            "confidence_score": 0.0
                        }
                    }
                    
                    # Save result to UserStateManager - use event_id as guild_id fallback
                    submit_result = SubmitPhotoDmResult(
                        success=result.success,
                        photo_id=result.photo_id,
                        message=result.message,
                        rate_limit_remaining=result.rate_limit_remaining,
                        next_allowed_submission=result.next_allowed_submission.isoformat() if result.next_allowed_submission else None,
                        vibe_check=response["vibe_check"],
                        event_id=event_id,
                        user_id=user_id,
                        photo_url=photo_url,
                        metadata=metadata
                    )
                    user_state_manager.add_model_entry(event_id, event_id, user_id, submit_result)
                    
                    logger.info(f"Final response without vibe check: {response}")
                    return response
            
            logger.warning(f"Photo submission failed: {result}")
            response = {
                "success": result.success,
                "photo_id": result.photo_id,
                "message": result.message,
                "rate_limit_remaining": result.rate_limit_remaining,
                "next_allowed_submission": result.next_allowed_submission.isoformat() if result.next_allowed_submission else None
            }
            
            # Save failed result to UserStateManager
            guild_id = metadata.get("guild_id", event_id) if metadata else event_id
            submit_result = SubmitPhotoDmResult(
                success=result.success,
                photo_id=result.photo_id,
                message=result.message,
                rate_limit_remaining=result.rate_limit_remaining,
                next_allowed_submission=result.next_allowed_submission.isoformat() if result.next_allowed_submission else None,
                event_id=event_id,
                user_id=user_id,
                photo_url=photo_url,
                metadata=metadata
            )
            user_state_manager.add_model_entry(guild_id, event_id, user_id, submit_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in submit_photo_dm: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            response = {
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_id = metadata.get("guild_id", event_id) if metadata else event_id
                submit_result = SubmitPhotoDmResult(
                    success=False,
                    message="Internal server error",
                    event_id=event_id,
                    user_id=user_id,
                    photo_url=photo_url,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, event_id, user_id, submit_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def activate_photo_collection(
        event_id: str,
        admin_user_id: str,
        rate_limit_hours: int = 1,
        max_hours_after_event: int = 24,
        event_start_time: Optional[str] = None,
        pre_event_photos: Optional[List[str]] = None,
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Activate photo collection for an event (Admin only).
        
        Args:
            event_id: The ID of the event
            admin_user_id: The Discord user ID of the admin
            rate_limit_hours: Hours between allowed submissions per user
            max_hours_after_event: Hours after event start to accept photos
            event_start_time: ISO timestamp of event start (optional)
            pre_event_photos: List of URLs for pre-event curation photos
            guild_id: The Discord guild ID (optional)
            
        Returns:
            Dict containing activation result
        """
        try:
            start_time = None
            if event_start_time:
                start_time = datetime.fromisoformat(event_start_time)
            
            config = service.create_event_config(
                event_id=event_id,
                admin_user_id=admin_user_id,
                activated=True,
                rate_limit_hours=rate_limit_hours,
                max_hours_after_event=max_hours_after_event,
                event_start_time=start_time,
                pre_event_photos=pre_event_photos or []
            )
            
            logger.info(f"Photo collection activated for event: {event_id} by {admin_user_id}")
            
            response = {
                "success": True,
                "message": "Photo collection activated for event",
                "config": {
                    "event_id": config.event_id,
                    "activated": config.activated,
                    "rate_limit_hours": config.rate_limit_hours,
                    "max_hours_after_event": config.max_hours_after_event,
                    "pre_event_photos_count": len(config.pre_event_photos)
                }
            }
            
            # Save result to UserStateManager
            guild_id_to_use = guild_id or event_id
            activate_result = ActivatePhotoCollectionResult(
                success=True,
                message="Photo collection activated for event",
                config=response["config"],
                event_id=event_id,
                admin_user_id=admin_user_id,
                rate_limit_hours=rate_limit_hours,
                max_hours_after_event=max_hours_after_event,
                event_start_time=event_start_time,
                pre_event_photos=pre_event_photos
            )
            user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, activate_result)
            
            # Update event.json with photo collection settings
            if guild_id:
                event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.activated", True)
                event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.admin_user_id", admin_user_id)
                event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.rate_limit_hours", rate_limit_hours)
                event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.max_hours_after_event", max_hours_after_event)
                if event_start_time:
                    event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.event_start_time", event_start_time)
                if pre_event_photos:
                    event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.pre_event_photos", pre_event_photos)
            
            return response
            
        except Exception as e:
            logger.error(f"Error activating photo collection: {e}")
            response = {
                "success": False,
                "message": "Failed to activate photo collection",
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_id_to_use = guild_id or event_id
                activate_result = ActivatePhotoCollectionResult(
                    success=False,
                    message="Failed to activate photo collection",
                    error=str(e),
                    event_id=event_id,
                    admin_user_id=admin_user_id,
                    rate_limit_hours=rate_limit_hours,
                    max_hours_after_event=max_hours_after_event,
                    event_start_time=event_start_time,
                    pre_event_photos=pre_event_photos
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, activate_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def deactivate_photo_collection(
        event_id: str,
        admin_user_id: str,
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Deactivate photo collection for an event (Admin only).
        
        Args:
            event_id: The ID of the event
            admin_user_id: The Discord user ID of the admin
            
        Returns:
            Dict containing deactivation result
        """
        try:
            config = service.update_event_config(
                event_id=event_id,
                admin_user_id=admin_user_id,
                activated=False
            )
            
            if not config:
                return {
                    "success": False,
                    "message": "Event configuration not found or access denied"
                }
            
            logger.info(f"Photo collection deactivated for event: {event_id} by {admin_user_id}")
            
            response = {
                "success": True,
                "message": "Photo collection deactivated for event"
            }
            
            # Save result to UserStateManager
            guild_id_to_use = guild_id or event_id
            deactivate_result = DeactivatePhotoCollectionResult(
                success=True,
                message="Photo collection deactivated for event",
                event_id=event_id,
                admin_user_id=admin_user_id
            )
            user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, deactivate_result)
            
            # Update event.json
            if guild_id:
                event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.activated", False)
            
            return response
            
        except ValueError as e:
            response = {
                "success": False,
                "message": str(e)
            }
            # Save error result
            try:
                guild_id_to_use = guild_id or event_id
                deactivate_result = DeactivatePhotoCollectionResult(
                    success=False,
                    message=str(e),
                    event_id=event_id,
                    admin_user_id=admin_user_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, deactivate_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            return response
        except Exception as e:
            logger.error(f"Error deactivating photo collection: {e}")
            response = {
                "success": False,
                "message": "Failed to deactivate photo collection",
                "error": str(e)
            }
            # Save error result
            try:
                guild_id_to_use = guild_id or event_id
                deactivate_result = DeactivatePhotoCollectionResult(
                    success=False,
                    message="Failed to deactivate photo collection",
                    error=str(e),
                    event_id=event_id,
                    admin_user_id=admin_user_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, deactivate_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            return response
    
    @mcp.tool()
    def update_photo_settings(
        event_id: str,
        admin_user_id: str,
        rate_limit_hours: Optional[int] = None,
        max_hours_after_event: Optional[int] = None,
        event_start_time: Optional[str] = None,
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update photo collection settings for an event (Admin only).
        
        Args:
            event_id: The ID of the event
            admin_user_id: The Discord user ID of the admin
            rate_limit_hours: New rate limit in hours (optional)
            max_hours_after_event: New max hours after event (optional)
            event_start_time: New event start time ISO string (optional)
            
        Returns:
            Dict containing update result
        """
        try:
            updates = {}
            
            if rate_limit_hours is not None:
                updates['rate_limit_hours'] = rate_limit_hours
            if max_hours_after_event is not None:
                updates['max_hours_after_event'] = max_hours_after_event
            if event_start_time is not None:
                updates['event_start_time'] = datetime.fromisoformat(event_start_time)
            
            config = service.update_event_config(
                event_id=event_id,
                admin_user_id=admin_user_id,
                **updates
            )
            
            if not config:
                return {
                    "success": False,
                    "message": "Event configuration not found or access denied"
                }
            
            logger.info(f"Photo settings updated for event: {event_id} by {admin_user_id}")
            
            response = {
                "success": True,
                "message": "Photo settings updated",
                "config": {
                    "rate_limit_hours": config.rate_limit_hours,
                    "max_hours_after_event": config.max_hours_after_event,
                    "event_start_time": config.event_start_time.isoformat() if config.event_start_time else None
                }
            }
            
            # Save result to UserStateManager
            guild_id_to_use = guild_id or event_id
            update_result = UpdatePhotoSettingsResult(
                success=True,
                message="Photo settings updated",
                config=response["config"],
                event_id=event_id,
                admin_user_id=admin_user_id,
                rate_limit_hours=rate_limit_hours,
                max_hours_after_event=max_hours_after_event,
                event_start_time=event_start_time
            )
            user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, update_result)
            
            # Update event.json
            if guild_id:
                if rate_limit_hours is not None:
                    event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.rate_limit_hours", rate_limit_hours)
                if max_hours_after_event is not None:
                    event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.max_hours_after_event", max_hours_after_event)
                if event_start_time is not None:
                    event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.event_start_time", event_start_time)
            
            return response
            
        except ValueError as e:
            response = {
                "success": False,
                "message": str(e)
            }
            # Save error result
            try:
                guild_id_to_use = guild_id or event_id
                update_result = UpdatePhotoSettingsResult(
                    success=False,
                    message=str(e),
                    event_id=event_id,
                    admin_user_id=admin_user_id,
                    rate_limit_hours=rate_limit_hours,
                    max_hours_after_event=max_hours_after_event,
                    event_start_time=event_start_time
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, update_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            return response
        except Exception as e:
            logger.error(f"Error updating photo settings: {e}")
            response = {
                "success": False,
                "message": "Failed to update photo settings",
                "error": str(e)
            }
            # Save error result
            try:
                guild_id_to_use = guild_id or event_id
                update_result = UpdatePhotoSettingsResult(
                    success=False,
                    message="Failed to update photo settings",
                    error=str(e),
                    event_id=event_id,
                    admin_user_id=admin_user_id,
                    rate_limit_hours=rate_limit_hours,
                    max_hours_after_event=max_hours_after_event,
                    event_start_time=event_start_time
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, update_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            return response
    
    @mcp.tool()
    def add_pre_event_photos(
        event_id: str,
        admin_user_id: str,
        photo_urls: List[str],
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add pre-event curation photos (Admin only).
        
        These photos will be used to determine relevance of user submissions.
        
        Args:
            event_id: The ID of the event
            admin_user_id: The Discord user ID of the admin
            photo_urls: List of URLs for pre-event photos
            guild_id: The Discord guild ID (optional)
            
        Returns:
            Dict containing addition result
        """
        try:
            config = service.get_event_config(event_id)
            if not config:
                response = {
                    "success": False,
                    "message": "Event configuration not found"
                }
                # Save error result to UserStateManager
                guild_id_to_use = guild_id or event_id
                add_result = AddPreEventPhotosResult(
                    success=False,
                    message="Event configuration not found",
                    event_id=event_id,
                    admin_user_id=admin_user_id,
                    photo_urls=photo_urls
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, add_result)
                return response
            
            if config.admin_user_id != admin_user_id:
                response = {
                    "success": False,
                    "message": "Only the event admin can add pre-event photos"
                }
                # Save error result to UserStateManager
                guild_id_to_use = guild_id or event_id
                add_result = AddPreEventPhotosResult(
                    success=False,
                    message="Only the event admin can add pre-event photos",
                    event_id=event_id,
                    admin_user_id=admin_user_id,
                    photo_urls=photo_urls
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, add_result)
                return response
            
            # Add new photos to existing list
            existing_photos = set(config.pre_event_photos)
            new_photos = [url for url in photo_urls if url not in existing_photos]
            
            updated_photos = config.pre_event_photos + new_photos
            
            config = service.update_event_config(
                event_id=event_id,
                admin_user_id=admin_user_id,
                pre_event_photos=updated_photos
            )
            
            logger.info(f"Pre-event photos added: {len(new_photos)} new photos for event {event_id}")
            
            response = {
                "success": True,
                "message": f"Added {len(new_photos)} new pre-event photos",
                "total_photos": len(updated_photos),
                "new_photos_added": len(new_photos)
            }
            
            # Save result to UserStateManager
            guild_id_to_use = guild_id or event_id
            add_result = AddPreEventPhotosResult(
                success=True,
                message=f"Added {len(new_photos)} new pre-event photos",
                total_photos=len(updated_photos),
                new_photos_added=len(new_photos),
                event_id=event_id,
                admin_user_id=admin_user_id,
                photo_urls=photo_urls
            )
            user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, add_result)
            
            # Update event.json with pre-event photos
            if guild_id:
                event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.pre_event_photos", updated_photos)
            
            return response
            
        except Exception as e:
            logger.error(f"Error adding pre-event photos: {e}")
            response = {
                "success": False,
                "message": "Failed to add pre-event photos",
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_id_to_use = guild_id or event_id
                add_result = AddPreEventPhotosResult(
                    success=False,
                    message="Failed to add pre-event photos",
                    error=str(e),
                    event_id=event_id,
                    admin_user_id=admin_user_id,
                    photo_urls=photo_urls
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, admin_user_id, add_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_photo_status(
        photo_id: str,
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the processing status of a submitted photo.
        
        Args:
            photo_id: The ID of the photo submission
            guild_id: The Discord guild ID (optional)
            
        Returns:
            Dict containing photo status and analysis
        """
        try:
            submission = service.get_photo_submission(photo_id)
            if not submission:
                response = {
                    "success": False,
                    "message": "Photo submission not found"
                }
                
                # Save error result to UserStateManager
                guild_id_to_use = guild_id or "unknown"
                status_result = GetPhotoStatusResult(
                    success=False,
                    message="Photo submission not found",
                    photo_id=photo_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, "unknown", "system", status_result)
                return response
            
            analysis = service.get_photo_analysis(photo_id)
            processing_state = service.get_processing_state(photo_id)
            
            logger.info(f"Photo status retrieved: {photo_id} - status: {submission.status}")
            
            result = {
                "success": True,
                "photo_id": photo_id,
                "status": submission.status,
                "submitted_at": submission.submitted_at.isoformat(),
                "user_id": submission.user_id,
                "event_id": submission.event_id
            }
            
            if processing_state:
                result["processing"] = {
                    "current_step": processing_state.current_step,
                    "progress": processing_state.progress,
                    "error": processing_state.error
                }
            
            if analysis:
                result["analysis"] = {
                    "quality_score": analysis.quality_score,
                    "quality_rating": analysis.quality_rating,
                    "relevance_score": analysis.relevance_score,
                    "relevance_rating": analysis.relevance_rating,
                    "overall_score": analysis.overall_score,
                    "content_analysis": analysis.content_analysis,
                    "reasoning": analysis.reasoning
                }
            
            # Save result to UserStateManager
            guild_id_to_use = guild_id or submission.event_id
            status_result = GetPhotoStatusResult(
                success=True,
                photo_id=photo_id,
                status=submission.status,
                submitted_at=submission.submitted_at.isoformat(),
                user_id=submission.user_id,
                event_id=submission.event_id,
                processing=result.get("processing"),
                analysis=result.get("analysis")
            )
            user_state_manager.add_model_entry(guild_id_to_use, submission.event_id, submission.user_id, status_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting photo status: {e}")
            response = {
                "success": False,
                "message": "Failed to get photo status",
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_id_to_use = guild_id or "unknown"
                status_result = GetPhotoStatusResult(
                    success=False,
                    message="Failed to get photo status",
                    error=str(e),
                    photo_id=photo_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, "unknown", "system", status_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_event_photo_summary(
        event_id: str,
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get summary of photo submissions for an event.
        
        Args:
            event_id: The ID of the event
            guild_id: The Discord guild ID (optional)
            
        Returns:
            Dict containing event photo summary
        """
        try:
            config = service.get_event_config(event_id)
            submissions = service.get_event_submissions(event_id)
            
            if not config:
                response = {
                    "success": False,
                    "message": "Event configuration not found"
                }
                
                # Save error result to UserStateManager
                guild_id_to_use = guild_id or event_id
                summary_result = GetEventPhotoSummaryResult(
                    success=False,
                    message="Event configuration not found",
                    event_id=event_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, "system", summary_result)
                return response
            
            # Count by status
            status_counts = {}
            for status in PhotoStatus:
                status_counts[status.value] = len([s for s in submissions if s.status == status])
            
            # Calculate statistics
            total_submissions = len(submissions)
            approved_submissions = [s for s in submissions if s.status == PhotoStatus.APPROVED]
            
            logger.info(f"Event photo summary retrieved: {event_id} - {total_submissions} submissions, {len(approved_submissions)} approved")
            
            result = {
                "success": True,
                "event_id": event_id,
                "activated": config.activated,
                "total_submissions": total_submissions,
                "status_breakdown": status_counts,
                "approved_count": len(approved_submissions),
                "config": {
                    "rate_limit_hours": config.rate_limit_hours,
                    "max_hours_after_event": config.max_hours_after_event,
                    "pre_event_photos_count": len(config.pre_event_photos),
                    "event_start_time": config.event_start_time.isoformat() if config.event_start_time else None
                }
            }
            
            # Add time window info
            if config.event_start_time:
                now = datetime.now(timezone.utc)
                time_remaining = config.event_start_time + timedelta(hours=config.max_hours_after_event) - now
                result["time_window"] = {
                    "accepting_submissions": service.check_time_window(event_id),
                    "time_remaining_hours": max(0, time_remaining.total_seconds() / 3600)
                }
            
            # Save result to UserStateManager
            guild_id_to_use = guild_id or event_id
            summary_result = GetEventPhotoSummaryResult(
                success=True,
                event_id=event_id,
                activated=config.activated,
                total_submissions=total_submissions,
                status_breakdown=status_counts,
                approved_count=len(approved_submissions),
                config=result["config"],
                time_window=result.get("time_window")
            )
            user_state_manager.add_model_entry(guild_id_to_use, event_id, "system", summary_result)
            
            logger.info(f'get_event_photo_summary result: {result}')
            return result
            
        except Exception as e:
            logger.error(f"Error getting event photo summary: {e}")
            response = {
                "success": False,
                "message": "Failed to get event photo summary",
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_id_to_use = guild_id or event_id
                summary_result = GetEventPhotoSummaryResult(
                    success=False,
                    message="Failed to get event photo summary",
                    error=str(e),
                    event_id=event_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, "system", summary_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    async def generate_event_slideshow(
        event_id: str,
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a slideshow from approved photos for an event.
        
        Args:
            event_id: The ID of the event
            guild_id: The Discord guild ID (optional)
            
        Returns:
            Dict containing slideshow data
        """
        try:
            slideshow = service.create_slideshow(event_id)
            
            if not slideshow:
                response = {
                    "success": False,
                    "message": "No approved photos available for slideshow or event not found"
                }
                
                # Save error result to UserStateManager
                guild_id_to_use = guild_id or event_id
                slideshow_result = GenerateEventSlideshowResult(
                    success=False,
                    message="No approved photos available for slideshow or event not found",
                    event_id=event_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, "system", slideshow_result)
                return response
            
            # Format photos for response
            photos_data = []
            for photo in slideshow.photos:
                photos_data.append({
                    "photo_id": photo.photo_id,
                    "photo_url": photo.photo_url,
                    "score": photo.score,
                    "user_id": photo.user_id,
                    "submitted_at": photo.submitted_at.isoformat(),
                    "caption": photo.caption
                })
            
            logger.info(f"Event slideshow generated: {slideshow.slideshow_id} for event {event_id} with {len(photos_data)} photos")
            
            result = {
                "success": True,
                "slideshow_id": slideshow.slideshow_id,
                "event_id": slideshow.event_id,
                "photos": photos_data,
                "total_submissions": slideshow.total_submissions,
                "accepted_count": slideshow.accepted_count,
                "rejected_count": slideshow.rejected_count,
                "created_at": slideshow.created_at.isoformat(),
                "message": f"Generated slideshow with {len(photos_data)} photos"
            }
            
            # Save result to UserStateManager
            guild_id_to_use = guild_id or event_id
            slideshow_result = GenerateEventSlideshowResult(
                success=True,
                message=f"Generated slideshow with {len(photos_data)} photos",
                slideshow_id=slideshow.slideshow_id,
                event_id=slideshow.event_id,
                photos=photos_data,
                total_submissions=slideshow.total_submissions,
                accepted_count=slideshow.accepted_count,
                rejected_count=slideshow.rejected_count,
                created_at=slideshow.created_at.isoformat()
            )
            user_state_manager.add_model_entry(guild_id_to_use, event_id, "system", slideshow_result)
            
            # Update event.json with slideshow data
            if guild_id:
                event_state_manager.append_to_array_field(guild_id, event_id, "slideshows", {
                    "slideshow_id": slideshow.slideshow_id,
                    "created_at": slideshow.created_at.isoformat(),
                    "photo_count": len(photos_data),
                    "accepted_count": slideshow.accepted_count,
                    "total_submissions": slideshow.total_submissions
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating slideshow: {e}")
            response = {
                "success": False,
                "message": "Failed to generate slideshow",
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_id_to_use = guild_id or event_id
                slideshow_result = GenerateEventSlideshowResult(
                    success=False,
                    message="Failed to generate slideshow",
                    error=str(e),
                    event_id=event_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id, "system", slideshow_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response
    
    @mcp.tool()
    def get_user_photo_history(
        user_id: str,
        event_id: Optional[str] = None,
        guild_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get photo submission history for a user.
        
        Args:
            user_id: The Discord user ID
            event_id: Optional event ID to filter by
            guild_id: The Discord guild ID (optional)
            
        Returns:
            Dict containing user's photo history
        """
        try:
            submissions = service.get_user_submissions(user_id, event_id)
            
            submissions_data = []
            for submission in submissions:
                analysis = service.get_photo_analysis(submission.photo_id)
                
                submission_data = {
                    "photo_id": submission.photo_id,
                    "event_id": submission.event_id,
                    "status": submission.status,
                    "submitted_at": submission.submitted_at.isoformat(),
                    "photo_url": submission.photo_url
                }
                
                if analysis:
                    submission_data["analysis"] = {
                        "overall_score": analysis.overall_score,
                        "quality_score": analysis.quality_score,
                        "relevance_score": analysis.relevance_score
                    }
                
                submissions_data.append(submission_data)
            
            logger.info(f"User photo history retrieved: {user_id} - {len(submissions)} submissions")
            
            result = {
                "success": True,
                "user_id": user_id,
                "total_submissions": len(submissions),
                "submissions": submissions_data
            }
            
            # Save result to UserStateManager
            guild_id_to_use = guild_id or event_id or "unknown"
            event_id_to_use = event_id or "all_events"
            history_result = GetUserPhotoHistoryResult(
                success=True,
                user_id=user_id,
                total_submissions=len(submissions),
                submissions=submissions_data,
                event_id=event_id
            )
            user_state_manager.add_model_entry(guild_id_to_use, event_id_to_use, user_id, history_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting user photo history: {e}")
            response = {
                "success": False,
                "message": "Failed to get user photo history",
                "error": str(e)
            }
            
            # Save error result to UserStateManager
            try:
                guild_id_to_use = guild_id or event_id or "unknown"
                event_id_to_use = event_id or "all_events"
                history_result = GetUserPhotoHistoryResult(
                    success=False,
                    message="Failed to get user photo history",
                    error=str(e),
                    user_id=user_id,
                    event_id=event_id
                )
                user_state_manager.add_model_entry(guild_id_to_use, event_id_to_use, user_id, history_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return response


async def _process_photo_async(service: PhotoVibeCheckService, processor: PhotoProcessor, photo_id: str):
    """Async function to process photo in background"""
    try:
        submission = service.get_photo_submission(photo_id)
        if not submission:
            logger.error(f"Photo submission {photo_id} not found for processing")
            return
        
        config = service.get_event_config(submission.event_id)
        if not config:
            logger.info(f"No event config found for event {submission.event_id}, creating default config")
            # Create a default config for this event
            config = service.create_event_config(
                event_id=submission.event_id,
                admin_user_id=submission.user_id,
                activated=True,
                rate_limit_hours=1,
                max_hours_after_event=24,
                event_start_time=None,
                pre_event_photos=[]
            )
        
        # Update status to processing
        submission.status = PhotoStatus.PROCESSING
        
        # Process photo
        analysis = await processor.process_photo(
            photo_id=photo_id,
            photo_url=submission.photo_url,
            event_id=submission.event_id,
            pre_event_photos=config.pre_event_photos
        )
        
        # Store analysis
        service.store_photo_analysis(analysis)
        
        logger.info(f"Completed processing photo {photo_id} with score {analysis.overall_score}")
        
    except Exception as e:
        logger.error(f"Error processing photo {photo_id}: {e}")
        
        # Update processing state with error
        if photo_id in service.processing_states:
            processing_state = service.processing_states[photo_id]
            processing_state.error = str(e)
            processing_state.current_step = "failed"
            processing_state.updated_at = datetime.now(timezone.utc)