import httpx
from loguru import logger
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from tlt.mcp_services.vibe_bit.models import (
    VibeElement, CanvasConfig, ElementPlacement, PlacementResponse, 
    RateLimitInfo, CanvasSnapshot, CanvasStats, ElementType,
    DEFAULT_COLOR_PALETTES
)

# Using loguru logger imported above

class VibeBitService:
    def __init__(self, event_manager_url: str = "http://localhost:8004"):
        # In-memory storage (in production, use database)
        self.canvas_configs: Dict[str, CanvasConfig] = {}  # event_id -> config
        self.vibe_elements: Dict[str, List[VibeElement]] = {}  # event_id -> elements
        self.rate_limits: Dict[str, RateLimitInfo] = {}  # user_id_event_id -> rate_info
        self.canvas_snapshots: Dict[str, List[CanvasSnapshot]] = {}  # event_id -> snapshots
        
        self.event_manager_url = event_manager_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def validate_rsvp(self, event_id: str, user_id: str) -> bool:
        """Validate that user has RSVP'd for the event"""
        try:
            response = await self.client.get(
                f"{self.event_manager_url}/event/{event_id}/rsvps"
            )
            if response.status_code == 200:
                event_data = response.json()
                rsvps = event_data.get("rsvps", [])
                
                # Check if user has any RSVP for this event
                user_rsvp = next((rsvp for rsvp in rsvps if rsvp["user_id"] == user_id), None)
                if user_rsvp:
                    # Consider attending, maybe, and tentative as valid for vibe bit placement
                    valid_statuses = ["attending", "maybe", "tentative"]
                    return user_rsvp["status"] in valid_statuses
                    
            return False
        except Exception as e:
            logger.error(f"Error validating RSVP: {e}")
            return False
    
    def check_rate_limit(self, user_id: str, event_id: str) -> Tuple[bool, Optional[RateLimitInfo]]:
        """Check if user is within rate limit for element placement"""
        rate_key = f"{user_id}_{event_id}"
        config = self.canvas_configs.get(event_id)
        
        if not config:
            return False, None
            
        rate_limit_hours = config.rate_limit_hours
        now = datetime.now(timezone.utc)
        
        if rate_key not in self.rate_limits:
            # First placement, allow it
            return True, None
            
        rate_info = self.rate_limits[rate_key]
        time_since_last = now - rate_info.last_placement
        
        if time_since_last.total_seconds() >= rate_limit_hours * 3600:
            # Enough time has passed
            return True, rate_info
        else:
            # Still within rate limit
            next_allowed = rate_info.last_placement + timedelta(hours=rate_limit_hours)
            rate_info.next_allowed = next_allowed
            return False, rate_info
    
    def check_time_window(self, event_id: str) -> bool:
        """Check if current time is within the allowed placement window"""
        config = self.canvas_configs.get(event_id)
        if not config or not config.activated:
            return False
            
        if not config.event_start_time:
            # If no start time set, assume placements are always allowed when activated
            return True
            
        now = datetime.now(timezone.utc)
        max_end_time = config.event_start_time + timedelta(hours=config.max_hours_after_event)
        
        # Allow placements from event start time until max_hours_after_event
        return config.event_start_time <= now <= max_end_time
    
    def check_position_valid(self, event_id: str, x: int, y: int) -> Tuple[bool, str]:
        """Check if position is valid for placement"""
        config = self.canvas_configs.get(event_id)
        if not config:
            return False, "Canvas configuration not found"
        
        # Check if position is within canvas bounds
        if x < 0 or x >= config.width or y < 0 or y >= config.height:
            return False, f"Position ({x}, {y}) is outside canvas bounds (0,0) to ({config.width-1},{config.height-1})"
        
        # Check for overlaps if not allowed
        if not config.allow_overlap:
            elements = self.vibe_elements.get(event_id, [])
            for element in elements:
                if element.position == (x, y):
                    return False, f"Position ({x}, {y}) is already occupied"
        
        return True, "Position is valid"
    
    def snap_to_grid(self, event_id: str, x: int, y: int) -> Tuple[int, int]:
        """Snap coordinates to grid"""
        config = self.canvas_configs.get(event_id)
        if not config:
            return x, y
        
        grid_size = config.grid_size
        snapped_x = (x // grid_size) * grid_size
        snapped_y = (y // grid_size) * grid_size
        
        return snapped_x, snapped_y
    
    def update_rate_limit(self, user_id: str, event_id: str):
        """Update rate limit tracking for user"""
        rate_key = f"{user_id}_{event_id}"
        now = datetime.now(timezone.utc)
        
        config = self.canvas_configs.get(event_id)
        if not config:
            return
            
        if rate_key in self.rate_limits:
            rate_info = self.rate_limits[rate_key]
            rate_info.placements_this_hour += 1
            rate_info.last_placement = now
        else:
            rate_info = RateLimitInfo(
                user_id=user_id,
                event_id=event_id,
                placements_this_hour=1,
                last_placement=now,
                next_allowed=now + timedelta(hours=config.rate_limit_hours)
            )
            self.rate_limits[rate_key] = rate_info
    
    async def place_element(self, placement: ElementPlacement) -> PlacementResponse:
        """Place an element on the canvas"""
        try:
            # Check if canvas is activated
            config = self.canvas_configs.get(placement.event_id)
            if not config or not config.activated:
                return PlacementResponse(
                    success=False,
                    message="Canvas is not currently active for this event"
                )
            
            # Check time window
            if not self.check_time_window(placement.event_id):
                return PlacementResponse(
                    success=False,
                    message="Element placement is outside the allowed time window"
                )
            
            # Validate RSVP
            has_rsvp = await self.validate_rsvp(placement.event_id, placement.user_id)
            if not has_rsvp:
                return PlacementResponse(
                    success=False,
                    message="Only users who have RSVP'd can place elements"
                )
            
            # Check rate limit
            within_limit, rate_info = self.check_rate_limit(placement.user_id, placement.event_id)
            if not within_limit:
                return PlacementResponse(
                    success=False,
                    message=f"Rate limit exceeded. Next placement allowed at {rate_info.next_allowed}",
                    next_allowed_placement=rate_info.next_allowed
                )
            
            # Snap coordinates to grid
            snapped_x, snapped_y = self.snap_to_grid(placement.event_id, placement.x, placement.y)
            
            # Check if position is valid
            position_valid, position_message = self.check_position_valid(placement.event_id, snapped_x, snapped_y)
            if not position_valid:
                return PlacementResponse(
                    success=False,
                    message=position_message
                )
            
            # Validate content based on element type
            if placement.element_type == ElementType.COLOR_BLOCK:
                if not self._is_valid_color(placement.content):
                    return PlacementResponse(
                        success=False,
                        message="Invalid color format. Use hex color codes like #FF0000"
                    )
            elif placement.element_type == ElementType.EMOJI:
                if not self._is_valid_emoji(placement.content):
                    return PlacementResponse(
                        success=False,
                        message="Invalid emoji format"
                    )
            
            # Create vibe element
            vibe_element = VibeElement(
                event_id=placement.event_id,
                user_id=placement.user_id,
                element_type=placement.element_type,
                content=placement.content,
                position=(snapped_x, snapped_y),
                metadata=placement.metadata or {}
            )
            
            # Store element
            if placement.event_id not in self.vibe_elements:
                self.vibe_elements[placement.event_id] = []
            self.vibe_elements[placement.event_id].append(vibe_element)
            
            # Update rate limit
            self.update_rate_limit(placement.user_id, placement.event_id)
            
            logger.info(f"Element placed: {vibe_element.element_id} by user {placement.user_id} at ({snapped_x}, {snapped_y})")
            
            return PlacementResponse(
                success=True,
                element_id=vibe_element.element_id,
                message="Element placed successfully",
                canvas_position=(snapped_x, snapped_y)
            )
            
        except Exception as e:
            logger.error(f"Error placing element: {e}")
            return PlacementResponse(
                success=False,
                message="Internal server error"
            )
    
    def _is_valid_color(self, color: str) -> bool:
        """Validate hex color format"""
        if not color.startswith('#'):
            return False
        if len(color) not in [4, 7]:  # #RGB or #RRGGBB
            return False
        try:
            int(color[1:], 16)
            return True
        except ValueError:
            return False
    
    def _is_valid_emoji(self, emoji: str) -> bool:
        """Basic emoji validation"""
        # Simple check for emoji length and Unicode ranges
        if len(emoji) > 10:  # Most emojis are 1-4 characters
            return False
        # In production, you might want more sophisticated emoji validation
        return len(emoji.strip()) > 0
    
    def create_canvas_config(
        self,
        event_id: str,
        admin_user_id: str,
        width: int = 256,
        height: int = 256,
        activated: bool = False,
        rate_limit_hours: int = 1,
        max_hours_after_event: int = 24,
        event_start_time: Optional[datetime] = None,
        background_color: str = "#FFFFFF",
        grid_size: int = 16,
        allow_overlap: bool = False
    ) -> CanvasConfig:
        """Create or update canvas configuration"""
        config = CanvasConfig(
            event_id=event_id,
            width=width,
            height=height,
            admin_user_id=admin_user_id,
            activated=activated,
            rate_limit_hours=rate_limit_hours,
            max_hours_after_event=max_hours_after_event,
            event_start_time=event_start_time,
            background_color=background_color,
            grid_size=grid_size,
            allow_overlap=allow_overlap
        )
        
        self.canvas_configs[event_id] = config
        logger.info(f"Created canvas config for {event_id} ({width}x{height}) by admin {admin_user_id}")
        
        return config
    
    def update_canvas_config(
        self,
        event_id: str,
        admin_user_id: str,
        **updates
    ) -> Optional[CanvasConfig]:
        """Update canvas configuration (admin only)"""
        config = self.canvas_configs.get(event_id)
        if not config:
            return None
            
        if config.admin_user_id != admin_user_id:
            raise ValueError("Only the event admin can update canvas configuration")
        
        # Update allowed fields
        allowed_updates = [
            'activated', 'rate_limit_hours', 'max_hours_after_event', 
            'event_start_time', 'background_color', 'allow_overlap'
        ]
        
        for key, value in updates.items():
            if key in allowed_updates and hasattr(config, key):
                setattr(config, key, value)
        
        config.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Updated canvas config for {event_id} by admin {admin_user_id}")
        return config
    
    def get_canvas_config(self, event_id: str) -> Optional[CanvasConfig]:
        """Get canvas configuration"""
        return self.canvas_configs.get(event_id)
    
    def get_canvas_elements(self, event_id: str) -> List[VibeElement]:
        """Get all elements on the canvas"""
        return self.vibe_elements.get(event_id, [])
    
    def get_user_elements(self, user_id: str, event_id: Optional[str] = None) -> List[VibeElement]:
        """Get all elements placed by a user"""
        all_elements = []
        
        if event_id:
            elements = self.vibe_elements.get(event_id, [])
            all_elements = [e for e in elements if e.user_id == user_id]
        else:
            for elements in self.vibe_elements.values():
                all_elements.extend([e for e in elements if e.user_id == user_id])
        
        return all_elements
    
    def create_canvas_snapshot(self, event_id: str, snapshot_type: str = "progress") -> Optional[CanvasSnapshot]:
        """Create a snapshot of the current canvas state"""
        config = self.canvas_configs.get(event_id)
        if not config:
            return None
        
        elements = self.get_canvas_elements(event_id)
        unique_users = len(set(element.user_id for element in elements))
        
        snapshot = CanvasSnapshot(
            canvas_id=config.canvas_id,
            event_id=event_id,
            width=config.width,
            height=config.height,
            elements=elements.copy(),
            total_placements=len(elements),
            unique_contributors=unique_users,
            snapshot_type=snapshot_type
        )
        
        # Store snapshot
        if event_id not in self.canvas_snapshots:
            self.canvas_snapshots[event_id] = []
        self.canvas_snapshots[event_id].append(snapshot)
        
        logger.info(f"Created {snapshot_type} snapshot for event {event_id} with {len(elements)} elements")
        return snapshot
    
    def get_canvas_stats(self, event_id: str) -> Optional[CanvasStats]:
        """Get canvas statistics"""
        config = self.canvas_configs.get(event_id)
        if not config:
            return None
        
        elements = self.get_canvas_elements(event_id)
        
        if not elements:
            return CanvasStats(
                event_id=event_id,
                canvas_id=config.canvas_id,
                total_elements=0,
                unique_users=0,
                elements_by_type={ElementType.EMOJI: 0, ElementType.COLOR_BLOCK: 0},
                coverage_percentage=0.0
            )
        
        # Calculate statistics
        unique_users = len(set(element.user_id for element in elements))
        
        # Count by type
        elements_by_type = {ElementType.EMOJI: 0, ElementType.COLOR_BLOCK: 0}
        emoji_counts = {}
        color_counts = {}
        user_counts = {}
        
        for element in elements:
            elements_by_type[element.element_type] += 1
            
            # Track user activity
            user_counts[element.user_id] = user_counts.get(element.user_id, 0) + 1
            
            # Track content usage
            if element.element_type == ElementType.EMOJI:
                emoji_counts[element.content] = emoji_counts.get(element.content, 0) + 1
            else:
                color_counts[element.content] = color_counts.get(element.content, 0) + 1
        
        # Calculate coverage
        total_grid_cells = (config.width // config.grid_size) * (config.height // config.grid_size)
        coverage_percentage = (len(elements) / total_grid_cells) * 100 if total_grid_cells > 0 else 0
        
        # Find most active user
        most_active_user = max(user_counts.items(), key=lambda x: x[1])[0] if user_counts else None
        
        # Find most used emoji and color
        most_used_emoji = max(emoji_counts.items(), key=lambda x: x[1])[0] if emoji_counts else None
        most_used_color = max(color_counts.items(), key=lambda x: x[1])[0] if color_counts else None
        
        # Create timeline (simplified - group by hour)
        timeline = {}
        for element in elements:
            hour_key = element.placed_at.replace(minute=0, second=0, microsecond=0)
            if hour_key not in timeline:
                timeline[hour_key] = 0
            timeline[hour_key] += 1
        
        placement_timeline = [
            {"time": time.isoformat(), "count": count}
            for time, count in sorted(timeline.items())
        ]
        
        return CanvasStats(
            event_id=event_id,
            canvas_id=config.canvas_id,
            total_elements=len(elements),
            unique_users=unique_users,
            elements_by_type=elements_by_type,
            coverage_percentage=min(100.0, coverage_percentage),
            most_active_user=most_active_user,
            most_used_emoji=most_used_emoji,
            most_used_color=most_used_color,
            placement_timeline=placement_timeline
        )
    
    def get_color_palettes(self) -> List[Dict]:
        """Get available color palettes"""
        return [palette.dict() for palette in DEFAULT_COLOR_PALETTES]