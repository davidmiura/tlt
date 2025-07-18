import io
from loguru import logger
import base64
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from tlt.mcp_services.vibe_bit.models import VibeElement, CanvasConfig, ElementType

# Using loguru logger imported above

class CanvasRenderer:
    def __init__(self):
        self.default_font_size = 12
        self.emoji_font_size = 14
        
    def render_canvas(
        self, 
        config: CanvasConfig, 
        elements: List[VibeElement],
        format: str = "PNG"
    ) -> bytes:
        """Render the canvas with all elements as an image"""
        try:
            # Create base image
            image = Image.new('RGB', (config.width, config.height), config.background_color)
            draw = ImageDraw.Draw(image)
            
            # Draw grid (optional - for debugging)
            if config.grid_size > 1:
                self._draw_grid(draw, config)
            
            # Draw all elements
            for element in elements:
                self._draw_element(draw, element, config)
            
            # Convert to bytes
            output = io.BytesIO()
            image.save(output, format=format)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error rendering canvas: {e}")
            # Return a simple error image
            return self._create_error_image(config.width, config.height)
    
    def render_canvas_with_overlay(
        self,
        config: CanvasConfig,
        elements: List[VibeElement],
        overlay_text: Optional[str] = None,
        show_stats: bool = False
    ) -> bytes:
        """Render canvas with optional overlay information"""
        try:
            # Create base canvas
            canvas_bytes = self.render_canvas(config, elements)
            image = Image.open(io.BytesIO(canvas_bytes))
            
            if overlay_text or show_stats:
                draw = ImageDraw.Draw(image)
                
                # Add overlay text
                if overlay_text:
                    self._add_overlay_text(draw, overlay_text, config.width, config.height)
                
                # Add statistics
                if show_stats:
                    stats_text = self._generate_stats_text(elements)
                    self._add_stats_overlay(draw, stats_text, config.width, config.height)
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format="PNG")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error rendering canvas with overlay: {e}")
            return self._create_error_image(config.width, config.height)
    
    def create_canvas_preview(
        self,
        config: CanvasConfig,
        elements: List[VibeElement],
        max_size: Tuple[int, int] = (512, 512)
    ) -> bytes:
        """Create a smaller preview version of the canvas"""
        try:
            # Calculate scale factor
            scale_x = max_size[0] / config.width
            scale_y = max_size[1] / config.height
            scale = min(scale_x, scale_y, 1.0)  # Don't upscale
            
            new_width = int(config.width * scale)
            new_height = int(config.height * scale)
            
            # Create scaled config
            preview_config = CanvasConfig(
                event_id=config.event_id,
                width=new_width,
                height=new_height,
                admin_user_id=config.admin_user_id,
                background_color=config.background_color,
                grid_size=max(1, int(config.grid_size * scale)),
                allow_overlap=config.allow_overlap
            )
            
            # Scale element positions
            scaled_elements = []
            for element in elements:
                scaled_element = VibeElement(
                    element_id=element.element_id,
                    event_id=element.event_id,
                    user_id=element.user_id,
                    element_type=element.element_type,
                    content=element.content,
                    position=(int(element.position[0] * scale), int(element.position[1] * scale)),
                    placed_at=element.placed_at,
                    metadata=element.metadata
                )
                scaled_elements.append(scaled_element)
            
            return self.render_canvas(preview_config, scaled_elements)
            
        except Exception as e:
            logger.error(f"Error creating canvas preview: {e}")
            return self._create_error_image(max_size[0], max_size[1])
    
    def _draw_grid(self, draw: ImageDraw.Draw, config: CanvasConfig):
        """Draw grid lines on the canvas"""
        grid_color = "#E0E0E0"  # Light gray
        
        # Vertical lines
        for x in range(0, config.width, config.grid_size):
            draw.line([(x, 0), (x, config.height)], fill=grid_color, width=1)
        
        # Horizontal lines
        for y in range(0, config.height, config.grid_size):
            draw.line([(0, y), (config.width, y)], fill=grid_color, width=1)
    
    def _draw_element(self, draw: ImageDraw.Draw, element: VibeElement, config: CanvasConfig):
        """Draw a single element on the canvas"""
        x, y = element.position
        
        if element.element_type == ElementType.COLOR_BLOCK:
            self._draw_color_block(draw, x, y, element.content, config.grid_size)
        elif element.element_type == ElementType.EMOJI:
            self._draw_emoji(draw, x, y, element.content, config.grid_size)
    
    def _draw_color_block(self, draw: ImageDraw.Draw, x: int, y: int, color: str, size: int):
        """Draw a colored block"""
        # Draw the main color block
        draw.rectangle(
            [x, y, x + size - 1, y + size - 1],
            fill=color,
            outline="#000000",
            width=1
        )
    
    def _draw_emoji(self, draw: ImageDraw.Draw, x: int, y: int, emoji: str, size: int):
        """Draw an emoji (simplified - uses text rendering)"""
        try:
            # Try to use a font that supports emoji
            # In production, you might want to use a proper emoji font
            font_size = min(size - 2, self.emoji_font_size)
            
            try:
                # Try to load a system font
                font = ImageFont.truetype("arial.ttf", font_size)
            except (OSError, IOError):
                try:
                    # Fallback to default font
                    font = ImageFont.load_default()
                except:
                    font = None
            
            # Center the emoji in the grid cell
            if font:
                bbox = draw.textbbox((0, 0), emoji, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                text_width = len(emoji) * 8  # Rough estimate
                text_height = 12
            
            text_x = x + (size - text_width) // 2
            text_y = y + (size - text_height) // 2
            
            # Draw background for better visibility
            draw.rectangle(
                [x, y, x + size - 1, y + size - 1],
                fill="#FFFFFF",
                outline="#CCCCCC",
                width=1
            )
            
            # Draw the emoji
            draw.text((text_x, text_y), emoji, fill="#000000", font=font)
            
        except Exception as e:
            logger.warning(f"Error drawing emoji {emoji}: {e}")
            # Fallback to a simple colored square
            draw.rectangle(
                [x, y, x + size - 1, y + size - 1],
                fill="#FFD700",  # Gold color as fallback
                outline="#000000",
                width=1
            )
    
    def _add_overlay_text(self, draw: ImageDraw.Draw, text: str, width: int, height: int):
        """Add overlay text to the image"""
        try:
            font = ImageFont.load_default()
            
            # Draw background for text
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Position at top center
            text_x = (width - text_width) // 2
            text_y = 10
            
            # Draw semi-transparent background
            draw.rectangle(
                [text_x - 5, text_y - 2, text_x + text_width + 5, text_y + text_height + 2],
                fill="#000000",
                outline=None
            )
            
            # Draw text
            draw.text((text_x, text_y), text, fill="#FFFFFF", font=font)
            
        except Exception as e:
            logger.warning(f"Error adding overlay text: {e}")
    
    def _add_stats_overlay(self, draw: ImageDraw.Draw, stats_text: str, width: int, height: int):
        """Add statistics overlay to the image"""
        try:
            font = ImageFont.load_default()
            
            # Position at bottom left
            lines = stats_text.split('\n')
            line_height = 15
            
            for i, line in enumerate(lines):
                y_pos = height - (len(lines) - i) * line_height - 10
                
                # Draw background for each line
                text_bbox = draw.textbbox((0, 0), line, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                
                draw.rectangle(
                    [5, y_pos - 2, text_width + 10, y_pos + line_height - 2],
                    fill="#000000",
                    outline=None
                )
                
                # Draw text
                draw.text((8, y_pos), line, fill="#FFFFFF", font=font)
                
        except Exception as e:
            logger.warning(f"Error adding stats overlay: {e}")
    
    def _generate_stats_text(self, elements: List[VibeElement]) -> str:
        """Generate statistics text for overlay"""
        if not elements:
            return "No elements placed"
        
        unique_users = len(set(element.user_id for element in elements))
        emoji_count = len([e for e in elements if e.element_type == ElementType.EMOJI])
        color_count = len([e for e in elements if e.element_type == ElementType.COLOR_BLOCK])
        
        return f"Elements: {len(elements)} | Users: {unique_users} | Emojis: {emoji_count} | Colors: {color_count}"
    
    def _create_error_image(self, width: int, height: int) -> bytes:
        """Create a simple error image"""
        try:
            image = Image.new('RGB', (width, height), '#FF0000')
            draw = ImageDraw.Draw(image)
            
            # Draw error text
            error_text = "Error rendering canvas"
            font = ImageFont.load_default()
            
            text_bbox = draw.textbbox((0, 0), error_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            text_x = (width - text_width) // 2
            text_y = (height - text_height) // 2
            
            draw.text((text_x, text_y), error_text, fill="#FFFFFF", font=font)
            
            output = io.BytesIO()
            image.save(output, format="PNG")
            return output.getvalue()
            
        except Exception:
            # Ultimate fallback - return minimal PNG
            return b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
    
    def canvas_to_base64(self, config: CanvasConfig, elements: List[VibeElement]) -> str:
        """Render canvas and return as base64 string"""
        canvas_bytes = self.render_canvas(config, elements)
        return base64.b64encode(canvas_bytes).decode('utf-8')
    
    def create_timelapse_frames(
        self,
        config: CanvasConfig,
        elements: List[VibeElement],
        frame_count: int = 10
    ) -> List[bytes]:
        """Create timelapse frames showing canvas evolution"""
        if not elements:
            return [self.render_canvas(config, [])]
        
        frames = []
        
        # Sort elements by placement time
        sorted_elements = sorted(elements, key=lambda e: e.placed_at)
        
        # Calculate elements per frame
        elements_per_frame = max(1, len(sorted_elements) // frame_count)
        
        for i in range(0, len(sorted_elements), elements_per_frame):
            frame_elements = sorted_elements[:i + elements_per_frame]
            frame_bytes = self.render_canvas_with_overlay(
                config, 
                frame_elements,
                overlay_text=f"Frame {len(frames) + 1}/{frame_count}",
                show_stats=True
            )
            frames.append(frame_bytes)
        
        # Ensure we have the final frame
        if frames and len(sorted_elements) > len(frames) * elements_per_frame:
            final_frame = self.render_canvas_with_overlay(
                config,
                sorted_elements,
                overlay_text="Final",
                show_stats=True
            )
            frames.append(final_frame)
        
        return frames