from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timezone
import uuid

class ElementType(str, Enum):
    EMOJI = "emoji"
    COLOR_BLOCK = "color_block"

class VibeElement(BaseModel):
    element_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    user_id: str
    element_type: ElementType
    content: str  # emoji character or hex color code
    position: Tuple[int, int]  # x, y coordinates on canvas
    placed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CanvasConfig(BaseModel):
    event_id: str
    canvas_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    width: int = Field(ge=32, le=1024)  # Canvas width in pixels
    height: int = Field(ge=32, le=1024)  # Canvas height in pixels
    admin_user_id: str
    activated: bool = False
    rate_limit_hours: int = 1  # Hours between placements per user
    max_hours_after_event: int = 24  # Hours after event start to accept placements
    event_start_time: Optional[datetime] = None
    background_color: str = "#FFFFFF"  # Default white background
    grid_size: int = 16  # Size of each placement grid cell in pixels
    allow_overlap: bool = False  # Whether elements can overlap
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ElementPlacement(BaseModel):
    event_id: str
    user_id: str
    element_type: ElementType
    content: str
    x: int
    y: int
    metadata: Optional[Dict[str, Any]] = None

class PlacementResponse(BaseModel):
    success: bool
    element_id: Optional[str] = None
    message: str
    canvas_position: Optional[Tuple[int, int]] = None
    rate_limit_remaining: Optional[int] = None
    next_allowed_placement: Optional[datetime] = None

class RateLimitInfo(BaseModel):
    user_id: str
    event_id: str
    placements_this_hour: int
    last_placement: datetime
    next_allowed: datetime

class CanvasSnapshot(BaseModel):
    canvas_id: str
    event_id: str
    width: int
    height: int
    elements: List[VibeElement]
    total_placements: int
    unique_contributors: int
    created_at: datetime
    snapshot_type: str  # "progress" or "final"

class CanvasStats(BaseModel):
    event_id: str
    canvas_id: str
    total_elements: int
    unique_users: int
    elements_by_type: Dict[ElementType, int]
    coverage_percentage: float  # Percentage of canvas filled
    most_active_user: Optional[str] = None
    most_used_emoji: Optional[str] = None
    most_used_color: Optional[str] = None
    placement_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ColorPalette(BaseModel):
    name: str
    colors: List[str]  # List of hex color codes
    description: str

# Predefined color palettes
DEFAULT_COLOR_PALETTES = [
    ColorPalette(
        name="vibrant",
        colors=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#FF8A80", "#82B1FF"],
        description="Vibrant and energetic colors"
    ),
    ColorPalette(
        name="pastel",
        colors=["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#E6BAFF", "#FFABAB", "#FFC3A0"],
        description="Soft pastel colors"
    ),
    ColorPalette(
        name="neon",
        colors=["#39FF14", "#FF073A", "#00FFFF", "#FF00FF", "#FFFF00", "#FF6600", "#9D00FF", "#00FF00"],
        description="Bright neon colors"
    ),
    ColorPalette(
        name="earth",
        colors=["#8B4513", "#DAA520", "#228B22", "#4682B4", "#CD853F", "#2F4F4F", "#808000", "#A0522D"],
        description="Natural earth tones"
    ),
    ColorPalette(
        name="monochrome",
        colors=["#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#FFFFFF", "#404040", "#808080"],
        description="Grayscale colors"
    )
]

# Common emoji sets
EMOJI_SETS = {
    "hearts": ["❤️", "🧡", "💛", "💚", "💙", "💜", "🤍", "🖤", "🤎", "💕"],
    "faces": ["😀", "😍", "🤔", "😎", "🥳", "😊", "🙂", "😄", "😆", "🤗"],
    "symbols": ["⭐", "✨", "🔥", "💯", "⚡", "🌟", "💫", "🎉", "🎊", "🎈"],
    "nature": ["🌸", "🌺", "🌻", "🌷", "🌹", "🍀", "🌿", "🌱", "🌳", "🍃"],
    "food": ["🍕", "🍔", "🍟", "🍿", "🍭", "🍪", "🧁", "🍰", "🎂", "🍩"],
    "activities": ["🎮", "🎵", "🎨", "📚", "⚽", "🏀", "🎯", "🎲", "🃏", "🎪"]
}

# Tool Result Models for UserStateManager
class VibeBitResult(BaseModel):
    success: bool
    element_id: Optional[str] = None
    message: str
    canvas_position: Optional[Tuple[int, int]] = None
    rate_limit_remaining: Optional[int] = None
    next_allowed_placement: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    user_id: str
    element_type: str
    content: str
    x: int
    y: int
    metadata: Optional[Dict[str, Any]] = None

class CreateVibeCanvasResult(BaseModel):
    success: bool
    message: str
    canvas_config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    admin_user_id: str
    width: int
    height: int
    activated: bool
    rate_limit_hours: int
    max_hours_after_event: int
    event_start_time: Optional[str] = None
    background_color: str
    grid_size: int
    allow_overlap: bool

class ActivateVibeCanvasResult(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    admin_user_id: str

class DeactivateVibeCanvasResult(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    admin_user_id: str

class UpdateVibeSettingsResult(BaseModel):
    success: bool
    message: str
    config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    admin_user_id: str
    rate_limit_hours: Optional[int] = None
    max_hours_after_event: Optional[int] = None
    event_start_time: Optional[str] = None
    background_color: Optional[str] = None
    allow_overlap: Optional[bool] = None

class GetVibeCanvasImageResult(BaseModel):
    success: bool
    message: Optional[str] = None
    canvas_image: Optional[str] = None
    format: Optional[str] = None
    dimensions: Optional[str] = None
    element_count: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    include_stats: bool

class GetVibeCanvasPreviewResult(BaseModel):
    success: bool
    message: Optional[str] = None
    preview_image: Optional[str] = None
    format: Optional[str] = None
    original_dimensions: Optional[str] = None
    element_count: Optional[int] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    max_size: int

class GetVibeCanvasStatsResult(BaseModel):
    success: bool
    message: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str

class GetUserVibeHistoryResult(BaseModel):
    success: bool
    message: Optional[str] = None
    user_id: Optional[str] = None
    total_placements: Optional[int] = None
    elements: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: Optional[str] = None

class GetColorPalettesResult(BaseModel):
    success: bool
    message: Optional[str] = None
    palettes: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GetEmojiSetsResult(BaseModel):
    success: bool
    message: Optional[str] = None
    emoji_sets: Optional[Dict[str, List[str]]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CreateVibeSnapshotResult(BaseModel):
    success: bool
    message: Optional[str] = None
    snapshot: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str
    snapshot_type: str