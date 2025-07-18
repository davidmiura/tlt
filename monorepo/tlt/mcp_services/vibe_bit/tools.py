import base64
import os
from loguru import logger
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from fastmcp import FastMCP
from tlt.mcp_services.vibe_bit.service import VibeBitService
from tlt.mcp_services.vibe_bit.canvas_renderer import CanvasRenderer
from tlt.mcp_services.vibe_bit.models import (
    ElementPlacement, ElementType, EMOJI_SETS,
    VibeBitResult,
    CreateVibeCanvasResult,
    ActivateVibeCanvasResult,
    DeactivateVibeCanvasResult,
    UpdateVibeSettingsResult,
    GetVibeCanvasImageResult,
    GetVibeCanvasPreviewResult,
    GetVibeCanvasStatsResult,
    GetUserVibeHistoryResult,
    GetColorPalettesResult,
    GetEmojiSetsResult,
    CreateVibeSnapshotResult
)
from tlt.shared.user_state_manager import UserStateManager
from tlt.shared.event_state_manager import EventStateManager

# Using loguru logger imported above

def register_tools(mcp: FastMCP, service: VibeBitService, renderer: CanvasRenderer):
    """Register all MCP tools for the vibe bit service"""
    
    # Initialize state managers
    guild_data_dir = os.getenv('GUILD_DATA_DIR', './guild_data')
    data_dir = os.path.join(guild_data_dir, 'data')
    user_state_manager = UserStateManager(data_dir)
    event_state_manager = EventStateManager(data_dir)
    
    @mcp.tool()
    async def vibe_bit(
        event_id: str,
        user_id: str,
        element_type: str,
        content: str,
        x: int,
        y: int,
        guild_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Place an emoji or colored block on the event canvas.
        
        This is the main tool called by the MCP gateway for vibe bit placement.
        Users can submit emojis or color blocks to be placed on a shared canvas.
        
        Args:
            event_id: The ID of the event
            user_id: The user ID placing the element
            element_type: Type of element ('emoji' or 'color_block')
            content: Emoji character or hex color code (e.g., '#FF0000')
            x: X coordinate on the canvas
            y: Y coordinate on the canvas
            guild_id: The Discord guild ID for state management
            metadata: Optional metadata (source info, etc.)
            
        Returns:
            Dict containing placement result and canvas position
        """
        try:
            logger.info(f"=== vibe_bit CALLED ===")
            logger.info(f"Event ID: {event_id}")
            logger.info(f"User ID: {user_id}")
            logger.info(f"Element Type: {element_type}")
            logger.info(f"Content: {content}")
            logger.info(f"Position: ({x}, {y})")
            logger.info(f"Guild ID: {guild_id}")
            logger.info(f"Metadata: {metadata}")
            
            # Validate element type
            if element_type not in ['emoji', 'color_block']:
                error_result = VibeBitResult(
                    success=False,
                    message="Invalid element_type. Use 'emoji' or 'color_block'",
                    event_id=event_id,
                    user_id=user_id,
                    element_type=element_type,
                    content=content,
                    x=x,
                    y=y,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, event_id, user_id, error_result)
                
                return {
                    "success": False,
                    "message": "Invalid element_type. Use 'emoji' or 'color_block'"
                }
            
            placement = ElementPlacement(
                event_id=event_id,
                user_id=user_id,
                element_type=ElementType(element_type),
                content=content,
                x=x,
                y=y,
                metadata=metadata
            )
            
            logger.info("Calling service.place_element...")
            result = await service.place_element(placement)
            logger.info(f"Service result: {result}")
            
            response = {
                "success": result.success,
                "message": result.message
            }
            
            if result.success:
                response.update({
                    "element_id": result.element_id,
                    "canvas_position": result.canvas_position,
                    "rate_limit_remaining": result.rate_limit_remaining
                })
                logger.info(f"Vibe bit placed successfully: {result.element_id} ({element_type}: {content}) by {user_id} at ({x}, {y}) for event {event_id}")
                
                # Save successful result to UserStateManager
                success_result = VibeBitResult(
                    success=result.success,
                    element_id=result.element_id,
                    message=result.message,
                    canvas_position=result.canvas_position,
                    rate_limit_remaining=result.rate_limit_remaining,
                    next_allowed_placement=result.next_allowed_placement.isoformat() if result.next_allowed_placement else None,
                    event_id=event_id,
                    user_id=user_id,
                    element_type=element_type,
                    content=content,
                    x=x,
                    y=y,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, event_id, user_id, success_result)
                
                # Update event.json with vibe bit placement
                event_state_manager.append_to_array_field(guild_id, event_id, "vibe_bit_placements", {
                    "element_id": result.element_id,
                    "user_id": user_id,
                    "element_type": element_type,
                    "content": content,
                    "position": result.canvas_position,
                    "placed_at": datetime.now(timezone.utc).isoformat(),
                    "metadata": metadata
                })
                
            else:
                if result.next_allowed_placement:
                    response["next_allowed_placement"] = result.next_allowed_placement.isoformat()
                
                # Save failed result to UserStateManager
                failed_result = VibeBitResult(
                    success=result.success,
                    message=result.message,
                    rate_limit_remaining=result.rate_limit_remaining,
                    next_allowed_placement=result.next_allowed_placement.isoformat() if result.next_allowed_placement else None,
                    event_id=event_id,
                    user_id=user_id,
                    element_type=element_type,
                    content=content,
                    x=x,
                    y=y,
                    metadata=metadata
                )
                user_state_manager.add_model_entry(guild_id, event_id, user_id, failed_result)
            
            logger.info(f"Final response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Error in vibe_bit tool: {e}")
            
            # Save error result to UserStateManager
            error_result = VibeBitResult(
                success=False,
                message="Internal server error",
                event_id=event_id,
                user_id=user_id,
                element_type=element_type,
                content=content,
                x=x,
                y=y,
                metadata=metadata
            )
            try:
                user_state_manager.add_model_entry(guild_id, event_id, user_id, error_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return {
                "success": False,
                "message": "Internal server error",
                "error": str(e)
            }
    
    @mcp.tool()
    def create_vibe_canvas(
        event_id: str,
        admin_user_id: str,
        guild_id: str,
        width: int = 256,
        height: int = 256,
        activated: bool = False,
        rate_limit_hours: int = 1,
        max_hours_after_event: int = 24,
        event_start_time: Optional[str] = None,
        background_color: str = "#FFFFFF",
        grid_size: int = 16,
        allow_overlap: bool = False
    ) -> Dict[str, Any]:
        """Create a vibe canvas for an event (Admin only).
        
        Args:
            event_id: The ID of the event
            admin_user_id: The user ID of the admin
            guild_id: The Discord guild ID for state management
            width: Canvas width in pixels (32-1024)
            height: Canvas height in pixels (32-1024)
            activated: Whether the canvas is active for placements
            rate_limit_hours: Hours between allowed placements per user
            max_hours_after_event: Hours after event start to accept placements
            event_start_time: ISO timestamp of event start (optional)
            background_color: Hex color for canvas background
            grid_size: Size of placement grid cells in pixels
            allow_overlap: Whether elements can overlap at same position
            
        Returns:
            Dict containing canvas creation result
        """
        try:
            logger.info(f"=== create_vibe_canvas CALLED ===")
            logger.info(f"Event ID: {event_id}")
            logger.info(f"Admin User ID: {admin_user_id}")
            logger.info(f"Guild ID: {guild_id}")
            logger.info(f"Dimensions: {width}x{height}")
            
            # Validate dimensions
            if not (32 <= width <= 1024 and 32 <= height <= 1024):
                error_result = CreateVibeCanvasResult(
                    success=False,
                    message="Canvas dimensions must be between 32x32 and 1024x1024 pixels",
                    event_id=event_id,
                    admin_user_id=admin_user_id,
                    width=width,
                    height=height,
                    activated=activated,
                    rate_limit_hours=rate_limit_hours,
                    max_hours_after_event=max_hours_after_event,
                    event_start_time=event_start_time,
                    background_color=background_color,
                    grid_size=grid_size,
                    allow_overlap=allow_overlap,
                    error="Invalid canvas dimensions"
                )
                user_state_manager.add_model_entry(guild_id, event_id, admin_user_id, error_result)
                
                return {
                    "success": False,
                    "message": "Canvas dimensions must be between 32x32 and 1024x1024 pixels"
                }
            
            start_time = None
            if event_start_time:
                try:
                    start_time = datetime.fromisoformat(event_start_time)
                except ValueError:
                    error_result = CreateVibeCanvasResult(
                        success=False,
                        message="Invalid event_start_time format. Use ISO format like '2024-01-15T18:00:00'",
                        event_id=event_id,
                        admin_user_id=admin_user_id,
                        width=width,
                        height=height,
                        activated=activated,
                        rate_limit_hours=rate_limit_hours,
                        max_hours_after_event=max_hours_after_event,
                        event_start_time=event_start_time,
                        background_color=background_color,
                        grid_size=grid_size,
                        allow_overlap=allow_overlap,
                        error="Invalid datetime format"
                    )
                    user_state_manager.add_model_entry(guild_id, event_id, admin_user_id, error_result)
                    
                    return {
                        "success": False,
                        "message": "Invalid event_start_time format. Use ISO format like '2024-01-15T18:00:00'"
                    }
            
            config = service.create_canvas_config(
                event_id=event_id,
                admin_user_id=admin_user_id,
                width=width,
                height=height,
                activated=activated,
                rate_limit_hours=rate_limit_hours,
                max_hours_after_event=max_hours_after_event,
                event_start_time=start_time,
                background_color=background_color,
                grid_size=grid_size,
                allow_overlap=allow_overlap
            )
            
            logger.info(f"Vibe canvas created successfully: {config.canvas_id} for event {event_id} by {admin_user_id}")
            
            canvas_config_dict = {
                "canvas_id": config.canvas_id,
                "event_id": config.event_id,
                "dimensions": f"{config.width}x{config.height}",
                "grid_size": config.grid_size,
                "activated": config.activated,
                "background_color": config.background_color,
                "allow_overlap": config.allow_overlap
            }
            
            # Save successful result to UserStateManager
            success_result = CreateVibeCanvasResult(
                success=True,
                message="Vibe canvas created successfully",
                canvas_config=canvas_config_dict,
                event_id=event_id,
                admin_user_id=admin_user_id,
                width=width,
                height=height,
                activated=activated,
                rate_limit_hours=rate_limit_hours,
                max_hours_after_event=max_hours_after_event,
                event_start_time=event_start_time,
                background_color=background_color,
                grid_size=grid_size,
                allow_overlap=allow_overlap
            )
            user_state_manager.add_model_entry(guild_id, event_id, admin_user_id, success_result)
            
            # Update event.json with canvas configuration
            event_state_manager.update_nested_field(guild_id, event_id, "vibe_canvas_config", {
                "canvas_id": config.canvas_id,
                "admin_user_id": admin_user_id,
                "width": width,
                "height": height,
                "activated": activated,
                "rate_limit_hours": rate_limit_hours,
                "max_hours_after_event": max_hours_after_event,
                "event_start_time": event_start_time,
                "background_color": background_color,
                "grid_size": grid_size,
                "allow_overlap": allow_overlap,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            
            return {
                "success": True,
                "message": "Vibe canvas created successfully",
                "canvas_config": canvas_config_dict
            }
            
        except Exception as e:
            logger.error(f"Error creating vibe canvas: {e}")
            
            # Save error result to UserStateManager
            error_result = CreateVibeCanvasResult(
                success=False,
                message="Failed to create vibe canvas",
                event_id=event_id,
                admin_user_id=admin_user_id,
                width=width,
                height=height,
                activated=activated,
                rate_limit_hours=rate_limit_hours,
                max_hours_after_event=max_hours_after_event,
                event_start_time=event_start_time,
                background_color=background_color,
                grid_size=grid_size,
                allow_overlap=allow_overlap,
                error=str(e)
            )
            try:
                user_state_manager.add_model_entry(guild_id, event_id, admin_user_id, error_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return {
                "success": False,
                "message": "Failed to create vibe canvas",
                "error": str(e)
            }
    
    @mcp.tool()
    def activate_vibe_canvas(
        event_id: str,
        admin_user_id: str,
        guild_id: str
    ) -> Dict[str, Any]:
        """Activate vibe canvas for an event (Admin only).
        
        Args:
            event_id: The ID of the event
            admin_user_id: The user ID of the admin
            guild_id: The Discord guild ID for state management
            
        Returns:
            Dict containing activation result
        """
        try:
            logger.info(f"=== activate_vibe_canvas CALLED ===")
            logger.info(f"Event ID: {event_id}")
            logger.info(f"Admin User ID: {admin_user_id}")
            logger.info(f"Guild ID: {guild_id}")
            
            config = service.update_canvas_config(
                event_id=event_id,
                admin_user_id=admin_user_id,
                activated=True
            )
            
            if not config:
                error_result = ActivateVibeCanvasResult(
                    success=False,
                    message="Canvas configuration not found or access denied",
                    event_id=event_id,
                    admin_user_id=admin_user_id,
                    error="Canvas not found or access denied"
                )
                user_state_manager.add_model_entry(guild_id, event_id, admin_user_id, error_result)
                
                return {
                    "success": False,
                    "message": "Canvas configuration not found or access denied"
                }
            
            logger.info(f"Vibe canvas activated for event {event_id} by {admin_user_id}")
            
            # Save successful result to UserStateManager
            success_result = ActivateVibeCanvasResult(
                success=True,
                message="Vibe canvas activated",
                event_id=event_id,
                admin_user_id=admin_user_id
            )
            user_state_manager.add_model_entry(guild_id, event_id, admin_user_id, success_result)
            
            # Update event.json with canvas activation
            event_state_manager.update_nested_field(guild_id, event_id, "vibe_canvas_config.activated", True)
            event_state_manager.update_nested_field(guild_id, event_id, "vibe_canvas_config.activated_at", datetime.now(timezone.utc).isoformat())
            event_state_manager.update_nested_field(guild_id, event_id, "vibe_canvas_config.activated_by", admin_user_id)
            
            return {
                "success": True,
                "message": "Vibe canvas activated"
            }
            
        except ValueError as e:
            error_result = ActivateVibeCanvasResult(
                success=False,
                message=str(e),
                event_id=event_id,
                admin_user_id=admin_user_id,
                error=str(e)
            )
            user_state_manager.add_model_entry(guild_id, event_id, admin_user_id, error_result)
            
            return {
                "success": False,
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Error activating vibe canvas: {e}")
            
            # Save error result to UserStateManager
            error_result = ActivateVibeCanvasResult(
                success=False,
                message="Failed to activate vibe canvas",
                event_id=event_id,
                admin_user_id=admin_user_id,
                error=str(e)
            )
            try:
                user_state_manager.add_model_entry(guild_id, event_id, admin_user_id, error_result)
            except Exception as state_error:
                logger.error(f"Failed to save error state: {state_error}")
            
            return {
                "success": False,
                "message": "Failed to activate vibe canvas",
                "error": str(e)
            }
    
    @mcp.tool()
    def deactivate_vibe_canvas(
        event_id: str,
        admin_user_id: str,
        guild_id: str
    ) -> Dict[str, Any]:
        """Deactivate vibe canvas for an event (Admin only).
        
        Args:
            event_id: The ID of the event
            admin_user_id: The user ID of the admin
            
        Returns:
            Dict containing deactivation result
        """
        try:
            config = service.update_canvas_config(
                event_id=event_id,
                admin_user_id=admin_user_id,
                activated=False
            )
            
            if not config:
                return {
                    "success": False,
                    "message": "Canvas configuration not found or access denied"
                }
            
            logger.info(f"Vibe canvas deactivated for event {event_id} by {admin_user_id}")
            
            return {
                "success": True,
                "message": "Vibe canvas deactivated"
            }
            
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Error deactivating vibe canvas: {e}")
            return {
                "success": False,
                "message": "Failed to deactivate vibe canvas",
                "error": str(e)
            }
    
    @mcp.tool()
    def update_vibe_settings(
        event_id: str,
        admin_user_id: str,
        guild_id: str,
        rate_limit_hours: Optional[int] = None,
        max_hours_after_event: Optional[int] = None,
        event_start_time: Optional[str] = None,
        background_color: Optional[str] = None,
        allow_overlap: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update vibe canvas settings (Admin only).
        
        Args:
            event_id: The ID of the event
            admin_user_id: The user ID of the admin
            rate_limit_hours: New rate limit in hours (optional)
            max_hours_after_event: New max hours after event (optional)
            event_start_time: New event start time ISO string (optional)
            background_color: New background color hex code (optional)
            allow_overlap: Whether to allow element overlap (optional)
            
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
                try:
                    updates['event_start_time'] = datetime.fromisoformat(event_start_time)
                except ValueError:
                    return {
                        "success": False,
                        "message": "Invalid event_start_time format"
                    }
            if background_color is not None:
                updates['background_color'] = background_color
            if allow_overlap is not None:
                updates['allow_overlap'] = allow_overlap
            
            config = service.update_canvas_config(
                event_id=event_id,
                admin_user_id=admin_user_id,
                **updates
            )
            
            if not config:
                return {
                    "success": False,
                    "message": "Canvas configuration not found or access denied"
                }
            
            logger.info(f"Vibe canvas settings updated for event {event_id} by {admin_user_id}")
            
            return {
                "success": True,
                "message": "Vibe canvas settings updated",
                "config": {
                    "rate_limit_hours": config.rate_limit_hours,
                    "max_hours_after_event": config.max_hours_after_event,
                    "event_start_time": config.event_start_time.isoformat() if config.event_start_time else None,
                    "background_color": config.background_color,
                    "allow_overlap": config.allow_overlap
                }
            }
            
        except ValueError as e:
            return {
                "success": False,
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"Error updating vibe settings: {e}")
            return {
                "success": False,
                "message": "Failed to update vibe settings",
                "error": str(e)
            }
    
    @mcp.tool()
    def get_vibe_canvas_image(
        event_id: str,
        guild_id: str,
        include_stats: bool = False,
        format: str = "base64"
    ) -> Dict[str, Any]:
        """Get the current vibe canvas as an image.
        
        Args:
            event_id: The ID of the event
            include_stats: Whether to include statistics overlay
            format: Return format ('base64' or 'url')
            
        Returns:
            Dict containing canvas image data
        """
        try:
            config = service.get_canvas_config(event_id)
            if not config:
                return {
                    "success": False,
                    "message": "Canvas configuration not found"
                }
            
            elements = service.get_canvas_elements(event_id)
            
            if include_stats:
                canvas_bytes = renderer.render_canvas_with_overlay(
                    config, elements, show_stats=True
                )
            else:
                canvas_bytes = renderer.render_canvas(config, elements)
            
            if format == "base64":
                canvas_b64 = base64.b64encode(canvas_bytes).decode('utf-8')
                logger.info(f"Vibe canvas image generated for event {event_id} (format: base64)")
                return {
                    "success": True,
                    "canvas_image": canvas_b64,
                    "format": "base64",
                    "dimensions": f"{config.width}x{config.height}",
                    "element_count": len(elements)
                }
            else:
                # In production, you might upload to a file service and return URL
                return {
                    "success": False,
                    "message": "URL format not implemented yet. Use 'base64' format."
                }
                
        except Exception as e:
            logger.error(f"Error getting vibe canvas image: {e}")
            return {
                "success": False,
                "message": "Failed to generate canvas image",
                "error": str(e)
            }
    
    @mcp.tool()
    def get_vibe_canvas_preview(
        event_id: str,
        guild_id: str,
        max_size: int = 512
    ) -> Dict[str, Any]:
        """Get a smaller preview of the vibe canvas.
        
        Args:
            event_id: The ID of the event
            max_size: Maximum dimension for the preview
            
        Returns:
            Dict containing preview image data
        """
        try:
            config = service.get_canvas_config(event_id)
            if not config:
                return {
                    "success": False,
                    "message": "Canvas configuration not found"
                }
            
            elements = service.get_canvas_elements(event_id)
            
            preview_bytes = renderer.create_canvas_preview(
                config, elements, (max_size, max_size)
            )
            
            preview_b64 = base64.b64encode(preview_bytes).decode('utf-8')
            
            logger.info(f"Vibe canvas preview generated for event {event_id}")
            
            return {
                "success": True,
                "preview_image": preview_b64,
                "format": "base64",
                "original_dimensions": f"{config.width}x{config.height}",
                "element_count": len(elements)
            }
            
        except Exception as e:
            logger.error(f"Error getting vibe canvas preview: {e}")
            return {
                "success": False,
                "message": "Failed to generate canvas preview",
                "error": str(e)
            }
    
    @mcp.tool()
    def get_vibe_canvas_stats(event_id: str, guild_id: str) -> Dict[str, Any]:
        """Get statistics for the vibe canvas.
        
        Args:
            event_id: The ID of the event
            
        Returns:
            Dict containing canvas statistics
        """
        try:
            stats = service.get_canvas_stats(event_id)
            if not stats:
                return {
                    "success": False,
                    "message": "Canvas not found"
                }
            
            logger.info(f"Vibe canvas stats retrieved for event {event_id} - {stats.total_elements} elements by {stats.unique_users} users")
            
            return {
                "success": True,
                "stats": {
                    "total_elements": stats.total_elements,
                    "unique_users": stats.unique_users,
                    "elements_by_type": {
                        "emoji": stats.elements_by_type.get(ElementType.EMOJI, 0),
                        "color_block": stats.elements_by_type.get(ElementType.COLOR_BLOCK, 0)
                    },
                    "coverage_percentage": stats.coverage_percentage,
                    "most_active_user": stats.most_active_user,
                    "most_used_emoji": stats.most_used_emoji,
                    "most_used_color": stats.most_used_color,
                    "placement_timeline": stats.placement_timeline
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting vibe canvas stats: {e}")
            return {
                "success": False,
                "message": "Failed to get canvas statistics",
                "error": str(e)
            }
    
    @mcp.tool()
    def get_user_vibe_history(
        user_id: str,
        guild_id: str,
        event_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get vibe placement history for a user.
        
        Args:
            user_id: The user ID
            event_id: Optional event ID to filter by
            
        Returns:
            Dict containing user's placement history
        """
        try:
            elements = service.get_user_elements(user_id, event_id)
            
            elements_data = []
            for element in elements:
                elements_data.append({
                    "element_id": element.element_id,
                    "event_id": element.event_id,
                    "element_type": element.element_type,
                    "content": element.content,
                    "position": element.position,
                    "placed_at": element.placed_at.isoformat()
                })
            
            logger.info(f"User vibe history retrieved: {user_id} - {len(elements)} placements")
            
            return {
                "success": True,
                "user_id": user_id,
                "total_placements": len(elements),
                "elements": elements_data
            }
            
        except Exception as e:
            logger.error(f"Error getting user vibe history: {e}")
            return {
                "success": False,
                "message": "Failed to get user placement history",
                "error": str(e)
            }
    
    @mcp.tool()
    def get_color_palettes(guild_id: str) -> Dict[str, Any]:
        """Get available color palettes for vibe bit placement.
        
        Returns:
            Dict containing available color palettes
        """
        try:
            palettes = service.get_color_palettes()
            
            logger.info(f"Color palettes retrieved: {len(palettes)} palettes")
            
            return {
                "success": True,
                "palettes": palettes
            }
            
        except Exception as e:
            logger.error(f"Error getting color palettes: {e}")
            return {
                "success": False,
                "message": "Failed to get color palettes",
                "error": str(e)
            }
    
    @mcp.tool()
    def get_emoji_sets(guild_id: str) -> Dict[str, Any]:
        """Get available emoji sets for vibe bit placement.
        
        Returns:
            Dict containing available emoji sets
        """
        try:
            logger.info(f"Emoji sets retrieved: {len(EMOJI_SETS)} emoji sets")
            
            return {
                "success": True,
                "emoji_sets": EMOJI_SETS
            }
            
        except Exception as e:
            logger.error(f"Error getting emoji sets: {e}")
            return {
                "success": False,
                "message": "Failed to get emoji sets",
                "error": str(e)
            }
    
    @mcp.tool()
    def create_vibe_snapshot(
        event_id: str,
        guild_id: str,
        snapshot_type: str = "progress"
    ) -> Dict[str, Any]:
        """Create a snapshot of the current canvas state.
        
        Args:
            event_id: The ID of the event
            snapshot_type: Type of snapshot ('progress' or 'final')
            
        Returns:
            Dict containing snapshot information
        """
        try:
            snapshot = service.create_canvas_snapshot(event_id, snapshot_type)
            
            if not snapshot:
                return {
                    "success": False,
                    "message": "Canvas not found"
                }
            
            logger.info(f"Vibe snapshot created: {snapshot.snapshot_id} for event {event_id}")
            
            return {
                "success": True,
                "snapshot": {
                    "canvas_id": snapshot.canvas_id,
                    "event_id": snapshot.event_id,
                    "dimensions": f"{snapshot.width}x{snapshot.height}",
                    "total_placements": snapshot.total_placements,
                    "unique_contributors": snapshot.unique_contributors,
                    "snapshot_type": snapshot.snapshot_type,
                    "created_at": snapshot.created_at.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating vibe snapshot: {e}")
            return {
                "success": False,
                "message": "Failed to create snapshot",
                "error": str(e)
            }