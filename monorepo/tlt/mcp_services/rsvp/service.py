import uuid
from loguru import logger
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from tlt.mcp_services.rsvp.models import (
    RSVPCreate, RSVPUpdate, RSVPResponse, UserRSVPSummary, 
    EventRSVPSummary, RSVPAnalytics
)

# Using loguru logger imported above

class RSVPService:
    """Service for managing user RSVP operations"""
    
    def __init__(self):
        # In-memory storage (in production, use database)
        self.rsvps: Dict[str, RSVPResponse] = {}  # rsvp_id -> RSVP
        self.user_rsvps: Dict[str, List[str]] = {}  # user_id -> list of rsvp_ids
        self.event_rsvps: Dict[str, List[str]] = {}  # event_id -> list of rsvp_ids
        
    def _is_valid_emoji(self, emoji_text: str) -> bool:
        """Validate that the input is a single valid emoji"""
        if not emoji_text:
            return False
        
        emoji_text = emoji_text.strip()
        
        # Check length - most emojis are 1-4 characters (including compound emojis)
        if len(emoji_text) > 4:
            return False
        
        # Basic Unicode ranges for emojis
        # This is a simplified check - in production you might want more comprehensive validation
        for char in emoji_text:
            code_point = ord(char)
            # Common emoji Unicode ranges
            if not (
                (0x1F600 <= code_point <= 0x1F64F) or  # Emoticons
                (0x1F300 <= code_point <= 0x1F5FF) or  # Misc Symbols and Pictographs
                (0x1F680 <= code_point <= 0x1F6FF) or  # Transport and Map
                (0x1F1E0 <= code_point <= 0x1F1FF) or  # Regional indicators
                (0x2600 <= code_point <= 0x26FF) or   # Misc symbols
                (0x2700 <= code_point <= 0x27BF) or   # Dingbats
                (0x1F900 <= code_point <= 0x1F9FF) or  # Supplemental Symbols and Pictographs
                (0x1F018 <= code_point <= 0x1F270) or  # Various symbols
                (0x238C <= code_point <= 0x2454) or    # Misc symbols
                (0xFE00 <= code_point <= 0xFE0F) or    # Variation selectors
                (0x200D == code_point)                 # Zero width joiner
            ):
                return False
        
        return True
    
    def create_rsvp(self, rsvp_data: RSVPCreate) -> RSVPResponse:
        """Create a new RSVP"""
        if not self._is_valid_emoji(rsvp_data.emoji):
            raise ValueError("Invalid emoji format. Please use a single emoji.")
        
        # Check if user already has an RSVP for this event
        existing_rsvp = self.get_user_rsvp_for_event(rsvp_data.user_id, rsvp_data.event_id)
        if existing_rsvp:
            # Update existing RSVP instead of creating a new one
            return self.update_rsvp(existing_rsvp.rsvp_id, RSVPUpdate(
                emoji=rsvp_data.emoji,
                response_time=rsvp_data.response_time,
                metadata=rsvp_data.metadata
            ))
        
        rsvp_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        rsvp = RSVPResponse(
            rsvp_id=rsvp_id,
            event_id=rsvp_data.event_id,
            user_id=rsvp_data.user_id,
            emoji=rsvp_data.emoji,
            response_time=rsvp_data.response_time or now,
            created_at=now,
            updated_at=now,
            metadata=rsvp_data.metadata
        )
        
        # Store RSVP
        self.rsvps[rsvp_id] = rsvp
        
        # Update indexes
        if rsvp_data.user_id not in self.user_rsvps:
            self.user_rsvps[rsvp_data.user_id] = []
        self.user_rsvps[rsvp_data.user_id].append(rsvp_id)
        
        if rsvp_data.event_id not in self.event_rsvps:
            self.event_rsvps[rsvp_data.event_id] = []
        self.event_rsvps[rsvp_data.event_id].append(rsvp_id)
        
        logger.info(f"Created RSVP {rsvp_id} for user {rsvp_data.user_id} to event {rsvp_data.event_id} with emoji {rsvp_data.emoji}")
        return rsvp
    
    def get_rsvp(self, rsvp_id: str) -> RSVPResponse:
        """Get RSVP by ID"""
        if rsvp_id not in self.rsvps:
            raise ValueError(f"RSVP {rsvp_id} not found")
        return self.rsvps[rsvp_id]
    
    def update_rsvp(self, rsvp_id: str, update_data: RSVPUpdate) -> RSVPResponse:
        """Update an existing RSVP"""
        if rsvp_id not in self.rsvps:
            raise ValueError(f"RSVP {rsvp_id} not found")
        
        rsvp = self.rsvps[rsvp_id]
        
        if update_data.emoji is not None:
            if not self._is_valid_emoji(update_data.emoji):
                raise ValueError("Invalid emoji format. Please use a single emoji.")
            rsvp.emoji = update_data.emoji
        
        if update_data.response_time is not None:
            rsvp.response_time = update_data.response_time
        
        if update_data.metadata is not None:
            rsvp.metadata.update(update_data.metadata)
        
        rsvp.updated_at = datetime.now(timezone.utc)
        
        logger.info(f"Updated RSVP {rsvp_id} with new emoji {rsvp.emoji}")
        return rsvp
    
    def delete_rsvp(self, rsvp_id: str) -> None:
        """Delete an RSVP"""
        if rsvp_id not in self.rsvps:
            raise ValueError(f"RSVP {rsvp_id} not found")
        
        rsvp = self.rsvps[rsvp_id]
        
        # Remove from indexes
        if rsvp.user_id in self.user_rsvps:
            self.user_rsvps[rsvp.user_id].remove(rsvp_id)
            if not self.user_rsvps[rsvp.user_id]:
                del self.user_rsvps[rsvp.user_id]
        
        if rsvp.event_id in self.event_rsvps:
            self.event_rsvps[rsvp.event_id].remove(rsvp_id)
            if not self.event_rsvps[rsvp.event_id]:
                del self.event_rsvps[rsvp.event_id]
        
        # Remove RSVP
        del self.rsvps[rsvp_id]
        
        logger.info(f"Deleted RSVP {rsvp_id}")
    
    def get_user_rsvp_for_event(self, user_id: str, event_id: str) -> Optional[RSVPResponse]:
        """Get user's RSVP for a specific event"""
        user_rsvp_ids = self.user_rsvps.get(user_id, [])
        
        for rsvp_id in user_rsvp_ids:
            rsvp = self.rsvps[rsvp_id]
            if rsvp.event_id == event_id:
                return rsvp
        
        return None
    
    def get_event_rsvps(self, event_id: str) -> EventRSVPSummary:
        """Get all RSVPs for an event"""
        rsvp_ids = self.event_rsvps.get(event_id, [])
        rsvps = [self.rsvps[rsvp_id] for rsvp_id in rsvp_ids]
        
        # Calculate emoji breakdown
        emoji_breakdown = {}
        for rsvp in rsvps:
            emoji_breakdown[rsvp.emoji] = emoji_breakdown.get(rsvp.emoji, 0) + 1
        
        # Calculate response rate (would need total invited from event service)
        response_rate = len(rsvps) / max(1, len(rsvps))  # Simplified for now
        
        return EventRSVPSummary(
            event_id=event_id,
            total_responses=len(rsvps),
            emoji_breakdown=emoji_breakdown,
            response_rate=response_rate,
            last_updated=datetime.now(timezone.utc),
            rsvps=rsvps
        )
    
    def get_user_rsvps(self, user_id: str) -> UserRSVPSummary:
        """Get all RSVPs for a user"""
        rsvp_ids = self.user_rsvps.get(user_id, [])
        rsvps = [self.rsvps[rsvp_id] for rsvp_id in rsvp_ids]
        
        # Group events by emoji
        events_by_emoji = {}
        for rsvp in rsvps:
            if rsvp.emoji not in events_by_emoji:
                events_by_emoji[rsvp.emoji] = []
            events_by_emoji[rsvp.emoji].append(rsvp.event_id)
        
        # Get recent RSVPs (last 10)
        recent_rsvps = sorted(rsvps, key=lambda x: x.updated_at, reverse=True)[:10]
        
        return UserRSVPSummary(
            user_id=user_id,
            total_rsvps=len(rsvps),
            events_by_emoji=events_by_emoji,
            recent_rsvps=recent_rsvps,
            last_updated=datetime.now(timezone.utc)
        )
    
    def update_user_rsvp(self, event_id: str, user_id: str, emoji: str, metadata: Dict[str, Any] = None) -> RSVPResponse:
        """Update or create RSVP for a user in an event"""
        if not self._is_valid_emoji(emoji):
            raise ValueError("Invalid emoji format. Please use a single emoji.")
        
        existing_rsvp = self.get_user_rsvp_for_event(user_id, event_id)
        
        if existing_rsvp:
            # Update existing RSVP
            return self.update_rsvp(existing_rsvp.rsvp_id, RSVPUpdate(
                emoji=emoji,
                response_time=datetime.now(timezone.utc),
                metadata=metadata or {}
            ))
        else:
            # Create new RSVP
            return self.create_rsvp(RSVPCreate(
                event_id=event_id,
                user_id=user_id,
                emoji=emoji,
                response_time=datetime.now(timezone.utc),
                metadata=metadata or {}
            ))
    
    def get_rsvp_analytics(self, event_id: str) -> RSVPAnalytics:
        """Get detailed RSVP analytics for an event"""
        rsvp_ids = self.event_rsvps.get(event_id, [])
        rsvps = [self.rsvps[rsvp_id] for rsvp_id in rsvp_ids]
        
        if not rsvps:
            return RSVPAnalytics(
                event_id=event_id,
                total_responses=0,
                emoji_breakdown={},
                response_timeline=[],
                unique_users=0
            )
        
        # Calculate emoji breakdown
        emoji_breakdown = {}
        for rsvp in rsvps:
            emoji_breakdown[rsvp.emoji] = emoji_breakdown.get(rsvp.emoji, 0) + 1
        
        # Find most popular emoji
        most_popular_emoji = max(emoji_breakdown.items(), key=lambda x: x[1])[0] if emoji_breakdown else None
        
        # Calculate response timeline (group by hour)
        timeline = {}
        for rsvp in rsvps:
            hour_key = rsvp.response_time.replace(minute=0, second=0, microsecond=0)
            if hour_key not in timeline:
                timeline[hour_key] = 0
            timeline[hour_key] += 1
        
        response_timeline = [
            {"time": time.isoformat(), "count": count}
            for time, count in sorted(timeline.items())
        ]
        
        # Calculate peak response time
        peak_response_time = None
        if timeline:
            peak_time = max(timeline.items(), key=lambda x: x[1])[0]
            peak_response_time = peak_time.isoformat()
        
        # Calculate average response time (simplified)
        if len(rsvps) > 1:
            first_response = min(rsvps, key=lambda x: x.response_time).response_time
            last_response = max(rsvps, key=lambda x: x.response_time).response_time
            avg_time_seconds = (last_response - first_response).total_seconds() / len(rsvps)
            average_response_time = avg_time_seconds / 3600  # Convert to hours
        else:
            average_response_time = None
        
        unique_users = len(set(rsvp.user_id for rsvp in rsvps))
        
        return RSVPAnalytics(
            event_id=event_id,
            total_responses=len(rsvps),
            emoji_breakdown=emoji_breakdown,
            response_timeline=response_timeline,
            peak_response_time=peak_response_time,
            average_response_time=average_response_time,
            most_popular_emoji=most_popular_emoji,
            unique_users=unique_users
        )
    
    def list_events_with_rsvps(self) -> List[str]:
        """List all events that have RSVPs"""
        return list(self.event_rsvps.keys())
    
    def get_rsvp_stats(self) -> Dict[str, Any]:
        """Get overall RSVP statistics"""
        total_rsvps = len(self.rsvps)
        total_events = len(self.event_rsvps)
        total_users = len(self.user_rsvps)
        
        # Count emoji usage across all RSVPs
        emoji_usage = {}
        for rsvp in self.rsvps.values():
            emoji_usage[rsvp.emoji] = emoji_usage.get(rsvp.emoji, 0) + 1
        
        return {
            "total_rsvps": total_rsvps,
            "total_events_with_rsvps": total_events,
            "total_users_with_rsvps": total_users,
            "global_emoji_usage": emoji_usage,
            "average_rsvps_per_event": total_rsvps / max(1, total_events),
            "average_rsvps_per_user": total_rsvps / max(1, total_users)
        }
    
    def process_rsvp_with_llm(self, 
                             event_id: str, 
                             user_id: str, 
                             rsvp_type: str, 
                             emoji: str, 
                             metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process RSVP reaction with LLM scoring to determine attendance likelihood"""
        try:
            # Import OpenAI here to avoid dependency issues if not available
            import os
            from openai import OpenAI
            
            # Get OpenAI API key from environment
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                logger.warning("OpenAI API key not found, using fallback scoring")
                return self._fallback_rsvp_scoring(event_id, user_id, rsvp_type, emoji, metadata)
            
            client = OpenAI(api_key=openai_api_key)
            
            # Get user's RSVP history for context
            user_rsvp_history = self.get_user_rsvps(user_id)
            
            # Prepare context for LLM
            context = {
                "event_id": event_id,
                "user_id": user_id,
                "rsvp_type": rsvp_type,
                "emoji": emoji,
                "metadata": metadata or {},
                "user_rsvp_history": user_rsvp_history.total_rsvps if user_rsvp_history else 0
            }
            
            # Create prompt for LLM
            prompt = f"""
            You are an expert at interpreting emoji reactions for event RSVPs. 
            
            Context:
            - Event ID: {event_id}
            - User ID: {user_id}
            - RSVP Action: {rsvp_type} (add/remove)
            - Emoji: {emoji}
            - User's RSVP History: {context['user_rsvp_history']} previous RSVPs
            
            Your task is to determine the likelihood (0.00 to 1.00) that this emoji reaction indicates the user is planning to attend the event.
            
            Consider these factors:
            1. Common emoji meanings in social contexts
            2. Whether the action is adding or removing the reaction
            3. Cultural context of emojis for event responses
            
            Scoring Guidelines:
            - 1.00: Definitely attending (✅, 👍, 🎉, 😊, 💯, etc.)
            - 0.80-0.90: Likely attending (👌, 🔥, 💪, 🙌, etc.)
            - 0.60-0.70: Possibly attending (🤔, 🤷, 😐, etc.)
            - 0.30-0.50: Unlikely attending (😕, 😔, 🤨, etc.)
            - 0.00-0.20: Definitely not attending (❌, 👎, 😢, 💀, etc.)
            
            If the action is "remove", interpret it as the user removing their previous sentiment.
            
            Respond with ONLY a JSON object in this format:
            {{
                "attendance_score": 0.85,
                "confidence": 0.90,
                "reasoning": "Brief explanation of the scoring decision",
                "emoji_interpretation": "What this emoji typically means in RSVP context"
            }}
            """
            
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert at interpreting emoji reactions for event RSVPs. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                import json
                llm_analysis = json.loads(response_text)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response as JSON: {response_text}")
                return self._fallback_rsvp_scoring(event_id, user_id, rsvp_type, emoji, metadata)
            
            # Validate response format
            required_fields = ["attendance_score", "confidence", "reasoning", "emoji_interpretation"]
            if not all(field in llm_analysis for field in required_fields):
                logger.error(f"LLM response missing required fields: {llm_analysis}")
                return self._fallback_rsvp_scoring(event_id, user_id, rsvp_type, emoji, metadata)
            
            # Ensure score is in valid range
            score = max(0.00, min(1.00, float(llm_analysis["attendance_score"])))
            confidence = max(0.00, min(1.00, float(llm_analysis["confidence"])))
            
            # Update or create RSVP with LLM analysis
            if rsvp_type == "add":
                rsvp_result = self.update_user_rsvp(event_id, user_id, emoji, {
                    **metadata,
                    "llm_analysis": llm_analysis,
                    "attendance_score": score,
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat()
                })
            else:  # remove
                # For remove actions, we might want to delete the RSVP or mark it as withdrawn
                existing_rsvp = self.get_user_rsvp_for_event(user_id, event_id)
                if existing_rsvp:
                    self.delete_rsvp(existing_rsvp.rsvp_id)
                    rsvp_result = None
                else:
                    rsvp_result = None
            
            return {
                "success": True,
                "rsvp_action": rsvp_type,
                "emoji": emoji,
                "attendance_score": score,
                "confidence": confidence,
                "reasoning": llm_analysis["reasoning"],
                "emoji_interpretation": llm_analysis["emoji_interpretation"],
                "rsvp_result": rsvp_result.dict() if rsvp_result else None,
                "analysis_method": "openai_llm"
            }
            
        except Exception as e:
            logger.error(f"Error in LLM RSVP processing: {e}")
            return self._fallback_rsvp_scoring(event_id, user_id, rsvp_type, emoji, metadata)
    
    def _fallback_rsvp_scoring(self, 
                              event_id: str, 
                              user_id: str, 
                              rsvp_type: str, 
                              emoji: str, 
                              metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fallback scoring method when LLM is not available"""
        
        # Simple rule-based scoring
        positive_emojis = {"✅", "👍", "🎉", "😊", "💯", "🔥", "👌", "💪", "🙌", "❤️", "😍", "🤩"}
        negative_emojis = {"❌", "👎", "😢", "💀", "😔", "😕", "🤨", "😞", "😪", "😴"}
        neutral_emojis = {"🤔", "🤷", "😐", "😑", "🙄", "😬", "😅"}
        
        if emoji in positive_emojis:
            score = 0.90
            interpretation = "Positive response indicating likely attendance"
        elif emoji in negative_emojis:
            score = 0.10
            interpretation = "Negative response indicating unlikely attendance"
        elif emoji in neutral_emojis:
            score = 0.50
            interpretation = "Neutral response indicating uncertain attendance"
        else:
            score = 0.60  # Default slightly positive for unknown emojis
            interpretation = "Unknown emoji, assuming mild positive intent"
        
        # Handle remove action
        if rsvp_type == "remove":
            # For remove, we still process but don't update RSVP
            existing_rsvp = self.get_user_rsvp_for_event(user_id, event_id)
            if existing_rsvp:
                self.delete_rsvp(existing_rsvp.rsvp_id)
                rsvp_result = None
            else:
                rsvp_result = None
        else:
            # For add, create/update RSVP
            rsvp_result = self.update_user_rsvp(event_id, user_id, emoji, {
                **(metadata or {}),
                "attendance_score": score,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return {
            "success": True,
            "rsvp_action": rsvp_type,
            "emoji": emoji,
            "attendance_score": score,
            "confidence": 0.70,  # Lower confidence for rule-based scoring
            "reasoning": f"Rule-based scoring: {interpretation}",
            "emoji_interpretation": interpretation,
            "rsvp_result": rsvp_result.dict() if rsvp_result else None,
            "analysis_method": "rule_based_fallback"
        }