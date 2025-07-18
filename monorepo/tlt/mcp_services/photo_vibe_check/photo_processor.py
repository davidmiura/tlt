import base64
from loguru import logger
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import pillow_avif
from PIL import Image
import io

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

from tlt.mcp_services.photo_vibe_check.models import PhotoAnalysis, PhotoQuality, PhotoRelevance
import os
import json
from pathlib import Path

# Using loguru logger imported above

class PhotoAnalysisOutput(BaseModel):
    quality_score: float = Field(ge=0.0, le=1.0, description="Photo quality score from 0 to 1")
    quality_rating: PhotoQuality = Field(description="Categorical quality rating")
    relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance score from 0 to 1")
    relevance_rating: PhotoRelevance = Field(description="Categorical relevance rating")
    size_check: bool = Field(description="Whether photo meets size requirements")
    content_analysis: str = Field(description="Description of photo content")
    reasoning: str = Field(description="Reasoning for scores and ratings")

class GenZVibeCheckOutput(BaseModel):
    vibe_score: float = Field(ge=0.0, le=1.0, description="GenZ vibe score from 0.0 (no vibe) to 1.0 (high vibe)")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in the vibe score assessment from 0.0 to 1.0")
    vibe_analysis: str = Field(description="Analysis of the photo's vibe check against promotional images")
    promotional_match: str = Field(description="How well the photo matches promotional content")
    reasoning: str = Field(description="Detailed reasoning for the vibe score and confidence")

class PhotoProcessingWorkflowState(TypedDict):
    photo_id: str
    photo_url: str
    event_id: str
    pre_event_photos: List[str]
    step: str
    progress: float
    photo_data: Optional[bytes]
    photo_analysis: Optional[PhotoAnalysisOutput]
    similarity_scores: Dict[str, float]
    overall_score: float
    error: Optional[str]
    messages: Annotated[List, add_messages]

class PhotoProcessor:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o",
            max_tokens=1000,
            temperature=0.1
        )
        
        self.analysis_parser = PydanticOutputParser(pydantic_object=PhotoAnalysisOutput)
        self.vibe_check_parser = PydanticOutputParser(pydantic_object=GenZVibeCheckOutput)
        
        # Create LangGraph workflow
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Create LangGraph workflow for photo processing"""
        workflow = StateGraph(PhotoProcessingWorkflowState)
        
        # Add nodes
        workflow.add_node("download_photo", self._download_photo)
        workflow.add_node("check_size_quality", self._check_size_quality)
        workflow.add_node("analyze_content", self._analyze_content)
        workflow.add_node("compare_similarity", self._compare_similarity)
        workflow.add_node("calculate_final_score", self._calculate_final_score)
        
        # Add edges
        workflow.add_edge("download_photo", "check_size_quality")
        workflow.add_edge("check_size_quality", "analyze_content")
        workflow.add_edge("analyze_content", "compare_similarity")
        workflow.add_edge("compare_similarity", "calculate_final_score")
        workflow.add_edge("calculate_final_score", END)
        
        # Set entry point
        workflow.set_entry_point("download_photo")
        
        return workflow.compile()
    
    async def process_photo(
        self, 
        photo_id: str, 
        photo_url: str, 
        event_id: str,
        pre_event_photos: List[str]
    ) -> PhotoAnalysis:
        """Process a photo through the complete analysis workflow"""
        
        initial_state = PhotoProcessingWorkflowState(
            photo_id=photo_id,
            photo_url=photo_url,
            event_id=event_id,
            pre_event_photos=pre_event_photos,
            step="starting",
            progress=0.0,
            photo_data=None,
            photo_analysis=None,
            similarity_scores={},
            overall_score=0.0,
            error=None,
            messages=[]
        )
        
        try:
            # Run the workflow
            result = await self.workflow.ainvoke(initial_state)
            
            if result.get("error"):
                raise Exception(result["error"])
            
            # Create PhotoAnalysis from result
            analysis_output = result["photo_analysis"]
            
            analysis = PhotoAnalysis(
                photo_id=photo_id,
                quality_score=analysis_output.quality_score,
                quality_rating=analysis_output.quality_rating,
                relevance_score=analysis_output.relevance_score,
                relevance_rating=analysis_output.relevance_rating,
                size_check=analysis_output.size_check,
                content_analysis=analysis_output.content_analysis,
                similarity_scores=result["similarity_scores"],
                overall_score=result["overall_score"],
                reasoning=analysis_output.reasoning
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing photo {photo_id}: {e}")
            
            # Return failed analysis
            return PhotoAnalysis(
                photo_id=photo_id,
                quality_score=0.0,
                quality_rating=PhotoQuality.UNUSABLE,
                relevance_score=0.0,
                relevance_rating=PhotoRelevance.NOT_RELEVANT,
                size_check=False,
                content_analysis=f"Processing failed: {str(e)}",
                similarity_scores={},
                overall_score=0.0,
                reasoning=f"Photo processing failed due to error: {str(e)}"
            )
    
    async def _download_photo(self, state: PhotoProcessingWorkflowState) -> PhotoProcessingWorkflowState:
        """Download and validate photo"""
        try:
            state["step"] = "downloading"
            state["progress"] = 0.1
            
            response = requests.get(state["photo_url"], timeout=30)
            response.raise_for_status()
            
            # Validate it's an image
            try:
                image = Image.open(io.BytesIO(response.content))
                image.verify()  # Verify it's a valid image
                state["photo_data"] = response.content
            except Exception as e:
                state["error"] = f"Invalid image format: {str(e)}"
                return state
            
            state["step"] = "downloaded"
            state["progress"] = 0.2
            
        except Exception as e:
            state["error"] = f"Failed to download photo: {str(e)}"
        
        return state
    
    async def _check_size_quality(self, state: PhotoProcessingWorkflowState) -> PhotoProcessingWorkflowState:
        """Check photo size and basic quality"""
        try:
            state["step"] = "checking_size"
            state["progress"] = 0.3
            
            if not state["photo_data"]:
                state["error"] = "No photo data available"
                return state
            
            image = Image.open(io.BytesIO(state["photo_data"]))
            width, height = image.size
            file_size = len(state["photo_data"])
            
            # Size requirements
            min_width, min_height = 640, 480  # Minimum resolution
            max_file_size = 10 * 1024 * 1024  # 10MB max
            
            size_check = (
                width >= min_width and 
                height >= min_height and 
                file_size <= max_file_size
            )
            
            # Basic quality assessment
            quality_score = min(1.0, (width * height) / (1920 * 1080))  # Normalize to 1080p
            
            if not size_check:
                quality_rating = PhotoQuality.UNUSABLE
                quality_score = 0.0
            elif width >= 1920 and height >= 1080:
                quality_rating = PhotoQuality.HIGH
            elif width >= 1280 and height >= 720:
                quality_rating = PhotoQuality.MEDIUM
            else:
                quality_rating = PhotoQuality.LOW
            
            # Store size check result
            if not hasattr(state, "photo_analysis") or state["photo_analysis"] is None:
                state["photo_analysis"] = PhotoAnalysisOutput(
                    quality_score=quality_score,
                    quality_rating=quality_rating,
                    relevance_score=0.0,
                    relevance_rating=PhotoRelevance.NOT_RELEVANT,
                    size_check=size_check,
                    content_analysis="",
                    reasoning=""
                )
            else:
                state["photo_analysis"].quality_score = quality_score
                state["photo_analysis"].quality_rating = quality_rating
                state["photo_analysis"].size_check = size_check
            
            state["step"] = "size_checked"
            state["progress"] = 0.4
            
        except Exception as e:
            state["error"] = f"Failed to check photo size/quality: {str(e)}"
        
        return state
    
    async def _analyze_content(self, state: PhotoProcessingWorkflowState) -> PhotoProcessingWorkflowState:
        """Analyze photo content using vision LLM"""
        try:
            state["step"] = "analyzing_content"
            state["progress"] = 0.6
            
            if not state["photo_data"]:
                state["error"] = "No photo data for analysis"
                return state
            
            # Convert photo to base64 for vision model (ensure JPEG format for OpenAI compatibility)
            photo_processed = self._ensure_jpeg_format(state["photo_data"])
            photo_base64 = base64.b64encode(photo_processed).decode()
            
            # Create analysis prompt
            system_prompt = """You are an expert photo analyst for event management. 
            Analyze this photo for quality, content, and relevance to events.
            
            Consider:
            1. Technical quality (clarity, lighting, composition)
            2. Content appropriateness for professional/social events
            3. Presence of people, activities, venues, or event-related items
            4. Overall aesthetic appeal
            
            Rate the photo's relevance for event photo collections."""
            
            user_prompt = f"""Analyze this photo and provide:
            1. Content description
            2. Quality assessment (0.0 to 1.0)
            3. Relevance to events (0.0 to 1.0)
            4. Reasoning for your scores
            
            {self.analysis_parser.get_format_instructions()}"""
            
            # Create message with image
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=[
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{photo_base64}"
                        }
                    }
                ])
            ]
            
            # Get analysis from LLM
            response = await self.llm.ainvoke(messages)
            analysis_result = self.analysis_parser.parse(response.content)
            
            # Update state with analysis
            if state["photo_analysis"] is None:
                state["photo_analysis"] = analysis_result
            else:
                # Update existing analysis
                state["photo_analysis"].content_analysis = analysis_result.content_analysis
                state["photo_analysis"].relevance_score = analysis_result.relevance_score
                state["photo_analysis"].relevance_rating = analysis_result.relevance_rating
                state["photo_analysis"].reasoning = analysis_result.reasoning
                # Keep existing quality scores from size check
            
            state["step"] = "content_analyzed"
            state["progress"] = 0.7
            
        except Exception as e:
            state["error"] = f"Failed to analyze photo content: {str(e)}"
        
        return state
    
    async def _compare_similarity(self, state: PhotoProcessingWorkflowState) -> PhotoProcessingWorkflowState:
        """Compare similarity to pre-event photos"""
        try:
            state["step"] = "comparing_similarity"
            state["progress"] = 0.8
            
            if not state["pre_event_photos"]:
                # No pre-event photos to compare against
                state["similarity_scores"] = {}
                state["step"] = "similarity_checked"
                state["progress"] = 0.9
                return state
            
            # For now, implement basic similarity (in production, use image embeddings)
            similarity_scores = {}
            
            # Simple similarity based on content analysis
            # In a real implementation, you would:
            # 1. Generate image embeddings for both photos
            # 2. Calculate cosine similarity
            # 3. Use CLIP or similar model for semantic similarity
            
            content_analysis = state["photo_analysis"].content_analysis.lower()
            
            for i, pre_photo_url in enumerate(state["pre_event_photos"]):
                # Placeholder similarity calculation
                # In reality, this would involve downloading and analyzing pre-event photos
                similarity = 0.5  # Default similarity
                
                # Basic keyword matching as placeholder
                event_keywords = ["venue", "logo", "banner", "stage", "swag", "staff", "host"]
                keyword_matches = sum(1 for keyword in event_keywords if keyword in content_analysis)
                similarity += (keyword_matches / len(event_keywords)) * 0.5
                
                similarity_scores[f"pre_event_{i}"] = min(1.0, similarity)
            
            state["similarity_scores"] = similarity_scores
            state["step"] = "similarity_checked"
            state["progress"] = 0.9
            
        except Exception as e:
            state["error"] = f"Failed to compare similarity: {str(e)}"
        
        return state
    
    async def _calculate_final_score(self, state: PhotoProcessingWorkflowState) -> PhotoProcessingWorkflowState:
        """Calculate final overall score"""
        try:
            state["step"] = "calculating_final_score"
            state["progress"] = 0.95
            
            analysis = state["photo_analysis"]
            if not analysis:
                state["error"] = "No analysis available for scoring"
                return state
            
            # Calculate weighted overall score
            quality_weight = 0.3
            relevance_weight = 0.4
            similarity_weight = 0.3
            
            quality_score = analysis.quality_score
            relevance_score = analysis.relevance_score
            
            # Average similarity score
            similarity_scores = state["similarity_scores"]
            avg_similarity = sum(similarity_scores.values()) / len(similarity_scores) if similarity_scores else 0.0
            
            overall_score = (
                quality_score * quality_weight +
                relevance_score * relevance_weight +
                avg_similarity * similarity_weight
            )
            
            # Apply size check penalty
            if not analysis.size_check:
                overall_score *= 0.5  # Penalize photos that don't meet size requirements
            
            state["overall_score"] = min(1.0, max(0.0, overall_score))
            state["step"] = "completed"
            state["progress"] = 1.0
            
        except Exception as e:
            state["error"] = f"Failed to calculate final score: {str(e)}"
        
        return state

    async def process_genz_vibe_check(
        self,
        photo_id: str,
        photo_url: str,
        event_id: str,
        user_id: str,
        guild_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process GenZ vibe check against promotional images"""
        try:
            logger.info(f"=== process_genz_vibe_check CALLED ===")
            logger.info(f"Photo ID: {photo_id}")
            logger.info(f"Photo URL: {photo_url}")
            logger.info(f"Event ID: {event_id}")
            logger.info(f"User ID: {user_id}")
            logger.info(f"Guild ID: {guild_id}")
            logger.info(f"Metadata: {metadata}")
            
            # 1. Build promotional images context
            logger.info("Step 1: Getting promotional images...")
            promotional_images = await self._get_promotional_images(guild_id, event_id)
            logger.info(f"Found {len(promotional_images)} promotional images")
            
            if not promotional_images:
                logger.warning(f"No promotional images found for event {event_id}, skipping vibe check")
                return {
                    "success": False,
                    "message": "No promotional images available for vibe check",
                    "vibe_score": 0.0,
                    "confidence_score": 0.0
                }
            
            # 2. Download and process user's image
            logger.info("Step 2: Downloading user photo...")
            user_photo_data = await self._download_photo_data(photo_url)
            if not user_photo_data:
                logger.error("Failed to download user photo")
                return {
                    "success": False,
                    "message": "Failed to download user photo",
                    "vibe_score": 0.0,
                    "confidence_score": 0.0
                }
            logger.info(f"User photo downloaded successfully: {len(user_photo_data)} bytes")
            
            # 3. Perform GenZ vibe check using GPT-4o
            logger.info("Step 3: Performing GenZ vibe check with GPT-4o...")
            user_photo_content_type = metadata.get("content_type", "")
            vibe_result = await self._perform_genz_vibe_check(
                user_photo_data, user_photo_content_type, promotional_images, event_id
            )
            logger.info(f"GPT-4o vibe check result: score={vibe_result.vibe_score}, confidence={vibe_result.confidence_score}")
            
            # 4. Record results in event.json
            logger.info("Step 4: Recording vibe check result to event.json...")
            await self._record_vibe_check_result(
                guild_id, event_id, user_id, photo_url, vibe_result
            )
            logger.info("Vibe check result recorded successfully")
            
            final_result = {
                "success": True,
                "vibe_score": vibe_result.vibe_score,
                "confidence_score": vibe_result.confidence_score,
                "vibe_analysis": vibe_result.vibe_analysis,
                "promotional_match": vibe_result.promotional_match,
                "reasoning": vibe_result.reasoning,
                "promotional_images_count": len(promotional_images)
            }
            
            logger.info(f"GenZ vibe check completed successfully: {photo_id} - final result: {final_result}")
            return final_result
            
        except Exception as e:
            logger.error(f"Error in GenZ vibe check for {photo_id}: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Vibe check processing failed: {str(e)}",
                "vibe_score": 0.0,
                "confidence_score": 0.0,
                "error": str(e)
            }

    async def _get_promotional_images(self, guild_id: str, event_id: str) -> List[bytes]:
        """Get all promotional images for the event"""
        try:
            # Build path to promotional images: guild_data/data/{guild_id}/{event_id}/{user_id}/promotion/
            data_dir = Path(os.getenv('GUILD_DATA_DIR', './guild_data'))
            event_dir = data_dir / "data" / guild_id / event_id
            
            promotional_images = []
            
            # Search all user directories for promotion subdirectories
            if event_dir.exists():
                for user_dir in event_dir.iterdir():
                    if user_dir.is_dir():
                        promotion_dir = user_dir / "promotion"
                        if promotion_dir.exists():
                            # Get all image files in promotion directory
                            for image_file in promotion_dir.glob("*"):
                                if image_file.suffix.lower() in ['.avif', '.jpg', '.jpeg', '.png', '.gif', '.webp']:
                                    try:
                                        with open(image_file, 'rb') as f:
                                            promotional_images.append(f.read())
                                        logger.info(f"Found promotional image: {image_file}")
                                    except Exception as e:
                                        logger.warning(f"Failed to read promotional image {image_file}: {e}")
            
            logger.info(f"Found {len(promotional_images)} promotional images for event {event_id}")
            return promotional_images
            
        except Exception as e:
            logger.error(f"Error getting promotional images: {e}")
            return []

    async def _download_photo_data(self, photo_url: str) -> Optional[bytes]:
        """Download photo data from URL"""
        try:
            response = requests.get(photo_url, timeout=30)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download photo from {photo_url}: {e}")
            return None

    async def _perform_genz_vibe_check(
        self, 
        user_photo_data: bytes, 
        user_photo_content_type: str,
        promotional_images: List[bytes], 
        event_id: str
    ) -> GenZVibeCheckOutput:
        """Perform GenZ vibe check using GPT-4o vision model"""
        try:
            logger.info(f"=== _perform_genz_vibe_check CALLED ===")
            logger.info(f"User photo data size: {len(user_photo_data)} bytes")
            logger.info(f"User photo content type: {user_photo_content_type}")
            logger.info(f"Promotional images count: {len(promotional_images)}")
            logger.info(f"Event ID: {event_id}")
            
            # Convert images to base64 with proper format detection
            logger.info("Converting user photo to base64...")
            
            # Detect and validate user photo format
            # user_image_format = self._detect_image_format(user_photo_data)
            user_image_format = user_photo_content_type
            logger.info(f"User photo format detected: {user_image_format}")
            
            # Convert to JPEG if needed for OpenAI compatibility
            user_photo_processed = self._ensure_jpeg_format(user_photo_data)
            user_photo_b64 = base64.b64encode(user_photo_processed).decode()
            logger.info(f"User photo base64 length: {len(user_photo_b64)}")
            
            logger.info("Converting promotional images to base64...")
            promo_photos_b64 = []
            for i, img_data in enumerate(promotional_images):
                promo_format = self._detect_image_format(img_data)
                logger.info(f"Promotional image {i+1} format: {promo_format}")
                
                promo_processed = self._ensure_jpeg_format(img_data)
                promo_b64 = base64.b64encode(promo_processed).decode()
                promo_photos_b64.append(promo_b64)
                
            logger.info(f"Promotional images base64 lengths: {[len(p) for p in promo_photos_b64]}")
            
            # Create GenZ vibe check prompt
            system_prompt = """You are a GenZ vibe check expert for event check-in systems! 🔥

Your job is to analyze if a user's photo submission matches the VIBE of an event based on promotional images. This replaces QR code check-ins - the photo IS the check-in method.

You should score based on:
1. **Visual Vibe Match**: Does the user photo match the aesthetic, style, colors, or setting of the promotional images?
2. **Event Participation**: Does it look like they're actually at/participating in this specific event?
3. **Authenticity**: Does it feel genuine (not a screenshot, old photo, or unrelated image)?
4. **Energy Match**: Does the photo capture the same energy/mood as the promotional content?

SCORING GUIDE (be strict but fair):
- 1.0 = Perfect vibe match, clearly at the event, captures the exact energy ✨
- 0.8-0.9 = Great match, definitely at event, good energy alignment 🔥  
- 0.6-0.7 = Good match, probably at event, decent vibe alignment 👍
- 0.4-0.5 = Okay match, might be at event, some vibe elements 🤔
- 0.2-0.3 = Poor match, unlikely at event, minimal vibe alignment 😬
- 0.0-0.1 = No match, definitely not at event, completely off-vibe ❌

Be authentic in your GenZ analysis - use natural language but be precise with scoring."""

            # Build message content with all images
            logger.info("Building message content for GPT-4o...")
            message_content = [
                {"type": "text", "text": f"Analyze this user's photo submission for event check-in vibe matching!\n\n{self.vibe_check_parser.get_format_instructions()}"},
                {
                    "type": "image_url", 
                    "image_url": {"url": f"data:image/jpeg;base64,{user_photo_b64}"}
                },
                {"type": "text", "text": f"\n📸 USER'S SUBMISSION ABOVE ⬆️\n\n🎯 PROMOTIONAL REFERENCE IMAGES BELOW ⬇️ ({len(promo_photos_b64)} total):"}
            ]
            
            # Add promotional images
            images_to_process = promo_photos_b64[:5]  # Limit to 5 promotional images
            logger.info(f"Adding {len(images_to_process)} promotional images to message content")
            for i, promo_b64 in enumerate(images_to_process):
                message_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{promo_b64}"}
                })
                message_content.append({
                    "type": "text", 
                    "text": f"^ Promotional Image {i+1}"
                })
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message_content)
            ]
            
            logger.info(f"Sending {len(messages)} messages to GPT-4o with {len(message_content)} content items")
            
            # Get vibe check from LLM
            logger.info("Calling GPT-4o LLM...")
            response = await self.llm.ainvoke(messages)
            logger.info(f"GPT-4o response received: {response.content[:200]}...")
            
            logger.info("Parsing GPT-4o response...")
            vibe_result = self.vibe_check_parser.parse(response.content)
            logger.info(f"Parsed vibe check result: score={vibe_result.vibe_score}, confidence={vibe_result.confidence_score}")
            
            return vibe_result
            
        except Exception as e:
            logger.error(f"Error in GenZ vibe check LLM call: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return GenZVibeCheckOutput(
                vibe_score=0.0,
                confidence_score=0.0,
                vibe_analysis=f"Vibe check failed: {str(e)}",
                promotional_match="Error in processing",
                reasoning=f"Technical error prevented vibe analysis: {str(e)}"
            )
    
    def _detect_image_format(self, image_data: bytes) -> str:
        """Detect image format from binary data"""
        try:
            image = Image.open(io.BytesIO(image_data))
            return image.format.lower() if image.format else "unknown"
        except Exception as e:
            logger.warning(f"Could not detect image format: {e}")
            return "unknown"
    
    def _ensure_jpeg_format(self, image_data: bytes) -> bytes:
        """Ensure image is in JPEG format for OpenAI compatibility"""
        try:
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if needed (for PNG with transparency, etc.)
            if image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save as JPEG
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=95)
            return output.getvalue()
            
        except Exception as e:
            logger.warning(f"Could not convert image to JPEG: {e}, returning original")
            return image_data

    async def _record_vibe_check_result(
        self, 
        guild_id: str, 
        event_id: str, 
        user_id: str, 
        photo_url: str, 
        vibe_result: GenZVibeCheckOutput
    ):
        """Record vibe check result in guild_data/data/<guild_id>/<event_id>/event.json"""
        try:
            # Build path to event.json
            data_dir = Path(os.getenv('GUILD_DATA_DIR', './guild_data'))
            event_dir = data_dir / "data" / guild_id / event_id
            event_json_path = event_dir / "event.json"
            
            # Ensure directory exists
            event_dir.mkdir(parents=True, exist_ok=True)
            
            # Load existing event data or create new
            event_data = {}
            if event_json_path.exists():
                try:
                    with open(event_json_path, 'r') as f:
                        event_data = json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to read existing event.json: {e}")
                    event_data = {}
            
            # Initialize vibe_checks if not exists
            if "vibe_checks" not in event_data:
                event_data["vibe_checks"] = []
            
            # Add new vibe check result
            vibe_check_entry = {
                "user_id": user_id,
                "photo_url": photo_url,
                "vibe_score": vibe_result.vibe_score,
                "confidence_score": vibe_result.confidence_score,
                "vibe_analysis": vibe_result.vibe_analysis,
                "promotional_match": vibe_result.promotional_match,
                "reasoning": vibe_result.reasoning,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "check_in_method": "photo_vibe_check"
            }
            
            # Remove any existing entry for this user (update instead of duplicate)
            event_data["vibe_checks"] = [
                vc for vc in event_data["vibe_checks"] 
                if vc.get("user_id") != user_id
            ]
            
            # Add the new entry
            event_data["vibe_checks"].append(vibe_check_entry)
            
            # Save back to file
            with open(event_json_path, 'w') as f:
                json.dump(event_data, f, indent=2)
            
            logger.info(f"Recorded vibe check result for user {user_id} in {event_json_path}")
            
        except Exception as e:
            logger.error(f"Failed to record vibe check result: {e}")
            # Don't fail the whole process if recording fails