# TLT Guild Data Schema Documentation

## Overview

This document describes the complete data schema and storage structure for the TLT (The Legendary Times) guild data system. The guild data directory serves as the primary persistent storage for all Discord guild events, user activities, and AI-generated content.

## Directory Structure

### Root Configuration
```bash
# Environment variable (default: ./guild_data)
GUILD_DATA_DIR=./guild_data
```

### Complete Directory Tree
```
guild_data/
├── guilds.json                    # Guild registry and metadata
├── settings.json                  # Global application settings
└── data/                          # Main data directory
    └── {guild_id}/                # Discord guild directory
        ├── {event_id}/            # Event-specific directory
        │   ├── event.json         # Event state and metadata
        │   └── {user_id}/         # User-specific event data
        │       ├── user.json      # User activity results
        │       ├── {timestamp}_{filename}.jpg  # User photos
        │       └── promotion/     # Promotional images
        │           └── {timestamp}_{filename}.jpg
        └── general/               # Non-event specific guild data
            └── {user_id}/
                └── user.json
```

## Path Structure Patterns

### 1. Guild Level
- **Path**: `guild_data/data/{guild_id}/`
- **Example**: `guild_data/data/{guild_id}/`
- **Purpose**: Discord server-specific data container

### 2. Event Level
- **Path**: `guild_data/data/{guild_id}/{event_id}/`
- **Example**: `guild_data/data/{guild_id}/{discord_id_2}/`
- **Purpose**: Event-specific data and user activities

### 3. User Level
- **Path**: `guild_data/data/{guild_id}/{event_id}/{user_id}/`
- **Example**: `guild_data/data/{guild_id}/{discord_id_2}/{discord_id_3}/`
- **Purpose**: User-specific activities within events

### 4. Promotional Media
- **Path**: `guild_data/data/{guild_id}/{event_id}/{user_id}/promotion/`
- **Example**: `guild_data/data/{guild_id}/{discord_id_2}/{discord_id_3}/promotion/`
- **Purpose**: AI vibe checking reference images

---

## Data Schema Organization

### Global Level Data

#### 1. Guild Registry (`guilds.json`)
**Location**: `guild_data/guilds.json`
**Purpose**: Central registry of all registered Discord guilds
**Pydantic Models**: `RegisteredGuild`, `GuildRegistrationData`

```json
{
  "{guild_id}": {
    "guild_id": "{guild_id}",
    "guild_name": "Development Server",
    "registered_at": "2025-07-17T12:29:00Z",
    "registered_by": "{discord_id_3}",
    "status": "active",
    "features": ["events", "photo_vibe_check", "vibe_canvas"],
    "settings": {
      "timezone": "UTC",
      "default_reminder_hours": [24, 2, 0.5]
    }
  }
}
```

#### 2. Global Settings (`settings.json`)
**Location**: `guild_data/settings.json`
**Purpose**: System-wide configuration settings
**Pydantic Models**: `GuildSettings`

```json
{
  "version": "1.0.0",
  "schema_version": "2025.1",
  "default_settings": {
    "photo_rate_limit_hours": 24,
    "max_photos_per_event": 50,
    "reminder_schedule": [24, 2, 0.5]
  }
}
```

### Event-Specific Data

#### 1. Event State (`event.json`)
**Location**: `guild_data/data/{guild_id}/{event_id}/event.json`
**Purpose**: Complete event lifecycle data and state management
**Pydantic Models**: `EventResponse`, `EventAnalytics`, `RSVPResponse`, `PhotoSubmission`, `VibeElement`

```json
{
  "topic": "Ice Cream Social",
  "location": "Molly Moon's",
  "time": "7pm Tomorrow",
  "creator_id": "{discord_id_3}",
  "guild_id": "{guild_id}",
  "channel_id": "{discord_id_4}",
  "event_id": "{discord_id_2}",
  "discord_message_id": "{discord_id_2}",
  "public_thread_id": "{discord_id_2}",
  "private_thread_id": "{discord_id_5}",
  "created_at": "2025-07-18T00:21:43.758224+00:00",
  "processed_rsvps": [
    {
      "user_id": "{discord_id_3}",
      "rsvp_type": "add",
      "emoji": "💯",
      "processed_at": "2025-07-18T00:22:41.685953+00:00",
      "llm_result": {
        "success": true,
        "rsvp_action": "add",
        "emoji": "💯",
        "attendance_score": 1.0,
        "confidence": 0.95,
        "reasoning": "The user is adding a 💯 emoji, which is commonly interpreted as a strong affirmation or enthusiasm for attending an event. Given that this is their first RSVP, the positive sentiment strongly indicates they plan to attend.",
        "emoji_interpretation": "The 💯 emoji typically signifies agreement, approval, or excitement, making it a clear indicator of intent to attend.",
        "rsvp_result": {
          "rsvp_id": "{uuid_7}",
          "event_id": "{discord_id_2}",
          "user_id": "{discord_id_3}",
          "emoji": "💯",
          "response_time": "2025-07-18 00:22:41.681689+00:00",
          "created_at": "2025-07-18 00:22:41.681786+00:00",
          "updated_at": "2025-07-18 00:22:41.681786+00:00",
          "metadata": {
            "source": "discord_rsvp_reaction",
            "rsvp_action": "add",
            "emoji": "💯",
            "event_topic": "Ice Cream Social",
            "event_creator_id": "{discord_id_3}",
            "event_location": "Molly Moon's",
            "event_time": "7pm Tomorrow",
            "llm_analysis": {
              "attendance_score": 1.0,
              "confidence": 0.95,
              "reasoning": "The user is adding a 💯 emoji, which is commonly interpreted as a strong affirmation or enthusiasm for attending an event. Given that this is their first RSVP, the positive sentiment strongly indicates they plan to attend.",
              "emoji_interpretation": "The 💯 emoji typically signifies agreement, approval, or excitement, making it a clear indicator of intent to attend."
            },
            "attendance_score": 1.0,
            "analysis_timestamp": "2025-07-18T00:22:41.681641+00:00"
          }
        },
        "analysis_method": "openai_llm"
      }
    }
  ],
  "vibe_checks": [
    {
      "user_id": "{discord_id_3}",
      "photo_url": "https://cdn.discordapp.com/attachments/.../1724189508-mm-wallingford-8.jpg",
      "vibe_score": 0.9,
      "confidence_score": 0.95,
      "vibe_analysis": "The user's photo matches the interior vibe of the promotional images, particularly the second one, with similar decor and setup.",
      "promotional_match": "Great match",
      "reasoning": "The user's photo shows an interior with a chalkboard menu and similar shelving, aligning well with the second promotional image. The aesthetic and setting are consistent, indicating the user is likely at the event location. The energy and style are cohesive, though the absence of people slightly reduces the perfect vibe match.",
      "timestamp": "2025-07-18T00:24:15.996842+00:00",
      "check_in_method": "photo_vibe_check"
    }
  ],
  "photo_submissions": [
    {
      "photo_id": "{uuid_8}",
      "user_id": "{discord_id_3}",
      "submitted_at": "2025-07-18T00:24:15.998064+00:00",
      "photo_url": "https://cdn.discordapp.com/attachments/.../1724189508-mm-wallingford-8.jpg",
      "status": "submitted",
      "vibe_check": {
        "success": true,
        "vibe_score": 0.9,
        "confidence_score": 0.95,
        "vibe_analysis": "The user's photo matches the interior vibe of the promotional images, particularly the second one, with similar decor and setup.",
        "promotional_match": "Great match",
        "reasoning": "The user's photo shows an interior with a chalkboard menu and similar shelving, aligning well with the second promotional image. The aesthetic and setting are consistent, indicating the user is likely at the event location. The energy and style are cohesive, though the absence of people slightly reduces the perfect vibe match.",
        "promotional_images_count": 2
      }
    }
  ]
}
```

### User-Specific Data

#### 1. User Activity Results (`user.json`)
**Location**: `guild_data/data/{guild_id}/{event_id}/{user_id}/user.json`
**Purpose**: Track all user tool execution results within an event
**Pydantic Models**: All `*Result` models from respective services

```json
{
  "user_id": "{discord_id_3}",
  "CreateEventResult": [
    {
      "success": true,
      "event_id": "{discord_id_2}",
      "message": "Event 'Ice Cream Social' created successfully",
      "event": {
        "event_id": "{discord_id_2}",
        "title": "Ice Cream Social",
        "description": "Location: Molly Moon's, Time: 7pm Tomorrow",
        "location": "Molly Moon's",
        "start_time": null,
        "end_time": null,
        "status": "draft",
        "created_by": "{discord_id_3}",
        "max_capacity": null,
        "require_approval": false,
        "created_at": "2025-07-18 00:22:03.409631+00:00",
        "updated_at": "2025-07-18 00:22:03.409631+00:00",
        "metadata": {
          "discord_message_id": "{discord_id_2}",
          "discord_thread_id": null,
          "discord_guild_id": "{guild_id}",
          "discord_channel_id": "{discord_id_4}",
          "discord_user_id": "{discord_id_3}",
          "discord_user_name": "",
          "source": "discord_create_event",
          "ambient_agent_processed": true,
          "original_time": "7pm Tomorrow"
        }
      },
      "timestamp": "2025-07-18 00:22:03.409954+00:00",
      "user_id": "{discord_id_3}",
      "guild_id": "{guild_id}"
    }
  ],
  "ProcessRsvpResult": [
    {
      "success": true,
      "result": {
        "success": true,
        "rsvp_action": "add",
        "emoji": "💯",
        "attendance_score": 1.0,
        "confidence": 0.95,
        "reasoning": "The user is adding a 💯 emoji, which is commonly interpreted as a strong affirmation or enthusiasm for attending an event. Given that this is their first RSVP, the positive sentiment strongly indicates they plan to attend.",
        "emoji_interpretation": "The 💯 emoji typically signifies agreement, approval, or excitement, making it a clear indicator of intent to attend.",
        "rsvp_result": {
          "rsvp_id": "{uuid_7}",
          "event_id": "{discord_id_2}",
          "user_id": "{discord_id_3}",
          "emoji": "💯",
          "response_time": "2025-07-18 00:22:41.681689+00:00",
          "created_at": "2025-07-18 00:22:41.681786+00:00",
          "updated_at": "2025-07-18 00:22:41.681786+00:00",
          "metadata": {
            "source": "discord_rsvp_reaction",
            "rsvp_action": "add",
            "emoji": "💯",
            "event_topic": "Ice Cream Social",
            "event_creator_id": "{discord_id_3}",
            "event_location": "Molly Moon's",
            "event_time": "7pm Tomorrow",
            "llm_analysis": {
              "attendance_score": 1.0,
              "confidence": 0.95,
              "reasoning": "The user is adding a 💯 emoji, which is commonly interpreted as a strong affirmation or enthusiasm for attending an event. Given that this is their first RSVP, the positive sentiment strongly indicates they plan to attend.",
              "emoji_interpretation": "The 💯 emoji typically signifies agreement, approval, or excitement, making it a clear indicator of intent to attend."
            },
            "attendance_score": 1.0,
            "analysis_timestamp": "2025-07-18T00:22:41.681641+00:00"
          }
        },
        "analysis_method": "openai_llm"
      },
      "message": "RSVP processed with LLM scoring for emoji 💯",
      "timestamp": "2025-07-18 00:22:41.684078+00:00",
      "event_id": "{discord_id_2}",
      "user_id": "{discord_id_3}",
      "rsvp_type": "add",
      "emoji": "💯"
    }
  ],
  "SubmitPhotoDmResult": [
    {
      "success": true,
      "photo_id": "{uuid_8}",
      "message": "Photo submitted successfully and queued for processing",
      "rate_limit_remaining": null,
      "next_allowed_submission": null,
      "vibe_check": {
        "success": true,
        "vibe_score": 0.9,
        "confidence_score": 0.95,
        "vibe_analysis": "The user's photo matches the interior vibe of the promotional images, particularly the second one, with similar decor and setup.",
        "promotional_match": "Great match",
        "reasoning": "The user's photo shows an interior with a chalkboard menu and similar shelving, aligning well with the second promotional image. The aesthetic and setting are consistent, indicating the user is likely at the event location. The energy and style are cohesive, though the absence of people slightly reduces the perfect vibe match.",
        "promotional_images_count": 2
      },
      "timestamp": "2025-07-18 00:24:15.997566+00:00",
      "event_id": "{discord_id_2}",
      "user_id": "{discord_id_3}",
      "photo_url": "https://cdn.discordapp.com/attachments/.../1724189508-mm-wallingford-8.jpg",
      "metadata": {
        "filename": "1724189508-mm-wallingford-8.jpg",
        "content_type": "image/avif",
        "size": 449054,
        "message_content": "The vibe is lit!",
        "guild_id": "{guild_id}",
        "channel_id": "{discord_id_2}",
        "source": "discord_thread_photo_submission",
        "message_id": "{discord_id_6}",
        "thread_id": "{discord_id_2}",
        "parent_channel_id": "{discord_id_4}",
        "event_message_id": "{discord_id_2}",
        "local_image_path": "guild_data/data/{guild_id}/{discord_id_2}/{discord_id_3}/20250717_172300_1724189508-mm-wallingford-8.jpg",
        "original_filename": "1724189508-mm-wallingford-8.jpg",
        "downloaded_at": "2025-07-18T00:23:00.796404+00:00"
      }
    }
  ]
}
```

#### 2. User Photos and Media
**Location**: `guild_data/data/{guild_id}/{event_id}/{user_id}/`
**Purpose**: Store user-uploaded photos and media files
**Naming Convention**: `{timestamp}_{original_filename}.jpg`

Examples:
- `20250717_172300_1724189508-mm-wallingford-8.jpg`
- `20250717_173045_user_selfie_at_event.jpg`

#### 3. Promotional Images
**Location**: `guild_data/data/{guild_id}/{event_id}/{user_id}/promotion/`
**Purpose**: AI vibe checking reference images uploaded by event creators
**Naming Convention**: `{timestamp}_{original_filename}.jpg`

Examples:
- `20250717_172222_1724217716-molly-moon-wallingford.jpg`
- `20250717_172255_event_venue_exterior.jpg`

---

## LLM Analysis Deep Dive

### RSVP Processing with LLM Analysis

The TLT system uses OpenAI's LLM to analyze emoji reactions and determine user attendance intent. Here's how the analysis works:

#### ProcessRsvpResult Structure
**Location**: `user.json` → `ProcessRsvpResult` array
**Purpose**: Tracks LLM analysis of user emoji reactions for event attendance

**Real Example from Guild Data:**
```json
{
  "success": true,
  "result": {
    "success": true,
    "rsvp_action": "add",
    "emoji": "💯",
    "attendance_score": 1.0,
    "confidence": 0.95,
    "reasoning": "The user is adding a 💯 emoji, which is commonly interpreted as a strong affirmation or enthusiasm for attending an event. Given that this is their first RSVP, the positive sentiment strongly indicates they plan to attend.",
    "emoji_interpretation": "The 💯 emoji typically signifies agreement, approval, or excitement, making it a clear indicator of intent to attend.",
    "analysis_method": "openai_llm"
  },
  "message": "RSVP processed with LLM scoring for emoji 💯"
}
```

#### LLM Analysis Fields
- **`attendance_score`**: Float 0.0-1.0 indicating likelihood of attendance
- **`confidence`**: Float 0.0-1.0 indicating LLM confidence in analysis
- **`reasoning`**: Detailed explanation of the emoji interpretation
- **`emoji_interpretation`**: Contextual meaning of the specific emoji
- **`analysis_method`**: Always "openai_llm" for LLM-processed RSVPs

### Photo Vibe Check Analysis

The system analyzes submitted photos against promotional images to determine "vibe match" using AI vision models.

#### SubmitPhotoDmResult Structure
**Location**: `user.json` → `SubmitPhotoDmResult` array
**Purpose**: Tracks photo submission and AI vibe analysis results

**Real Example from Guild Data:**
```json
{
  "success": true,
  "photo_id": "{uuid_8}",
  "message": "Photo submitted successfully and queued for processing",
  "vibe_check": {
    "success": true,
    "vibe_score": 0.9,
    "confidence_score": 0.95,
    "vibe_analysis": "The user's photo matches the interior vibe of the promotional images, particularly the second one, with similar decor and setup.",
    "promotional_match": "Great match",
    "reasoning": "The user's photo shows an interior with a chalkboard menu and similar shelving, aligning well with the second promotional image. The aesthetic and setting are consistent, indicating the user is likely at the event location. The energy and style are cohesive, though the absence of people slightly reduces the perfect vibe match.",
    "promotional_images_count": 2
  }
}
```

#### Vibe Check Analysis Fields
- **`vibe_score`**: Float 0.0-1.0 indicating photo-to-promotional match quality
- **`confidence_score`**: Float 0.0-1.0 indicating AI confidence in analysis
- **`vibe_analysis`**: Brief summary of the visual match assessment
- **`promotional_match`**: Qualitative assessment ("Great match", "Good match", etc.)
- **`reasoning`**: Detailed explanation of visual similarity analysis
- **`promotional_images_count`**: Number of promotional images compared against

### Event-Level Aggregated Data

#### processed_rsvps Array
**Location**: `event.json` → `processed_rsvps` array
**Purpose**: Event-level aggregation of all RSVP processing results

**Real Example from Guild Data:**
```json
{
  "user_id": "{discord_id_3}",
  "rsvp_type": "add",
  "emoji": "💯",
  "processed_at": "2025-07-18T00:22:41.685953+00:00",
  "llm_result": {
    "success": true,
    "rsvp_action": "add",
    "emoji": "💯",
    "attendance_score": 1.0,
    "confidence": 0.95,
    "reasoning": "The user is adding a 💯 emoji, which is commonly interpreted as a strong affirmation or enthusiasm for attending an event. Given that this is their first RSVP, the positive sentiment strongly indicates they plan to attend.",
    "emoji_interpretation": "The 💯 emoji typically signifies agreement, approval, or excitement, making it a clear indicator of intent to attend.",
    "analysis_method": "openai_llm"
  }
}
```

#### vibe_checks Array
**Location**: `event.json` → `vibe_checks` array
**Purpose**: Event-level aggregation of all photo vibe check results

**Real Example from Guild Data:**
```json
{
  "user_id": "{discord_id_3}",
  "photo_url": "https://cdn.discordapp.com/attachments/.../1724189508-mm-wallingford-8.jpg",
  "vibe_score": 0.9,
  "confidence_score": 0.95,
  "vibe_analysis": "The user's photo matches the interior vibe of the promotional images, particularly the second one, with similar decor and setup.",
  "promotional_match": "Great match",
  "reasoning": "The user's photo shows an interior with a chalkboard menu and similar shelving, aligning well with the second promotional image. The aesthetic and setting are consistent, indicating the user is likely at the event location. The energy and style are cohesive, though the absence of people slightly reduces the perfect vibe match.",
  "timestamp": "2025-07-18T00:24:15.996842+00:00",
  "check_in_method": "photo_vibe_check"
}
```

### AI Analysis Patterns

#### Common Attendance Scores
- **1.0**: Strong positive indicators (💯, ✅, 🎉, 👍)
- **0.8-0.9**: Moderate positive indicators (😊, 👌, 🤝)
- **0.5-0.7**: Neutral or ambiguous indicators (🤔, 🤷)
- **0.2-0.4**: Negative indicators (❌, 👎, 😞)
- **0.0-0.1**: Strong negative indicators (🚫, 💔)

#### Common Vibe Scores
- **0.9-1.0**: Excellent match - clearly at event location with strong visual similarity
- **0.7-0.8**: Good match - likely at event location with some visual similarity
- **0.5-0.6**: Moderate match - possibly at event location but unclear
- **0.3-0.4**: Poor match - unlikely at event location
- **0.0-0.2**: No match - clearly not at event location

#### Confidence Scoring
- **0.9-1.0**: High confidence - clear indicators, unambiguous context
- **0.7-0.8**: Moderate confidence - some ambiguity but generally clear
- **0.5-0.6**: Low confidence - significant ambiguity or unclear context
- **0.3-0.4**: Very low confidence - highly ambiguous or conflicting signals

---

## State Management Systems

### EventStateManager
**File**: `tlt/shared/event_state_manager.py`
**Purpose**: Manages event-level data persistence and operations

#### Key Methods:
- `add_model_entry()` - Add Pydantic model instances to event data
- `update_event_field()` - Update single event fields
- `append_to_array_field()` - Add items to event arrays (RSVPs, photos)
- `update_nested_field()` - Update nested configuration fields
- `remove_from_array_field()` - Remove items from event arrays
- `list_model_entries()` - Retrieve typed model instances from event data

#### Usage Pattern:
```python
event_state_manager = EventStateManager(guild_data_dir)
event_state_manager.append_to_array_field(guild_id, event_id, "rsvps", rsvp_data)
event_state_manager.update_nested_field(guild_id, event_id, "photo_collection.activated", True)
```

### UserStateManager
**File**: `tlt/shared/user_state_manager.py`
**Purpose**: Manages user-specific data persistence within events

#### Key Methods:
- `add_model_entry()` - Add tool execution results to user data
- `list_model_entries()` - Retrieve typed results by model class
- `update_model_entry()` - Update existing user data entries
- `delete_model_entry()` - Remove user data entries
- `list_model_types()` - Get available model types for user

#### Usage Pattern:
```python
user_state_manager = UserStateManager(guild_data_dir)
user_state_manager.add_model_entry(guild_id, event_id, user_id, create_event_result)
```

---

## Data Access Patterns

### 1. Event Creation Flow
```
1. Discord Adapter → CloudEvent → TLT Service
2. TLT Service → MCP Gateway → Event Manager
3. Event Manager → EventStateManager.add_model_entry()
4. EventStateManager → event.json (event_manager_data)
5. UserStateManager → user.json (CreateEventResult)
```

### 2. RSVP Processing Flow
```
1. Discord Reaction → CloudEvent → TLT Service
2. TLT Service → MCP Gateway → RSVP Service
3. RSVP Service → EventStateManager.append_to_array_field()
4. EventStateManager → event.json (rsvps array)
5. UserStateManager → user.json (ProcessRsvpResult)
```

### 3. Photo Vibe Check Flow
```
1. Discord DM → CloudEvent → TLT Service
2. TLT Service → MCP Gateway → Photo Vibe Check
3. Photo Vibe Check → LangGraph Workflow
4. File Storage → guild_data/data/{guild_id}/{event_id}/{user_id}/
5. EventStateManager → event.json (photo_submissions array)
6. UserStateManager → user.json (SubmitPhotoDmResult)
```

---

## File System Operations

### Directory Creation
All directories are created automatically using:
```python
path.mkdir(parents=True, exist_ok=True)
```

### File Naming Conventions
- **Event Data**: `event.json`
- **User Data**: `user.json`
- **Photos**: `{YYYYMMDD}_{HHMMSS}_{original_filename}.jpg`
- **Promotional Images**: Same as photos, in `/promotion/` subdirectory

### JSON Serialization
All data is serialized using:
```python
json.dump(data, file, indent=2, default=str)
```

The `default=str` parameter ensures datetime objects are properly serialized as ISO strings.

---

## Configuration and Environment

### Environment Variables
```bash
# Guild data directory location
GUILD_DATA_DIR=./guild_data

# Alternative for production
GUILD_DATA_DIR=/var/lib/tlt/guild_data
```

### Service Integration
All MCP services use the same configuration:
```python
guild_data_dir = os.getenv('GUILD_DATA_DIR', './guild_data')
data_dir = os.path.join(guild_data_dir, 'data')
```

### Backup and Recovery
The file-based storage system supports:
- Simple file system backups
- Git-based version control
- Incremental backup strategies
- Cross-platform compatibility

---

## Security Considerations

### Data Isolation
- Each guild has isolated data directories
- User data is scoped to specific events
- No cross-guild data leakage possible

### File Permissions
- Standard file system permissions apply
- Service accounts should have appropriate access
- Sensitive data is stored in structured JSON format

### Privacy Protection
- User IDs are Discord snowflakes (non-PII)
- Photos are stored locally, not in cloud services
- Data retention is controlled by file system policies

---

This schema provides a comprehensive, scalable, and maintainable data structure for the TLT event management system, supporting all current features while allowing for future expansion.