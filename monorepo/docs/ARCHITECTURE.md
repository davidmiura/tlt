# TLT Architecture Documentation

## Overview

TLT is a microservices-based event management platform that combines Discord bot integration with AI-powered photo vibe checking and collaborative features. The system is built using LangGraph for agent orchestration, FastMCP for service communication, and modern Python/TypeScript technologies.

## System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        DC[Discord Client]
        DB[Dashboard Browser]
        SC[Slack Client]
    end
    
    subgraph "Reverse Proxy"
        CADDY[Caddy Reverse Proxy<br/>Port 80/443]
    end
    
    subgraph "Adapter Layer"
        DA[Discord Adapter<br/>FastAPI + Discord.py<br/>Port 8001]
        SA[Slack Adapter<br/>FastAPI<br/>Port 8002]
    end
    
    subgraph "Gateway Layer"
        GW[MCP Gateway<br/>FastAPI REST<br/>Port 8003]
    end
    
    subgraph "MCP Services Layer"
        GM[Guild Manager<br/>FastMCP<br/>Port 8009]
        EM[Event Manager<br/>FastMCP 2.0<br/>Port 8004]
        PVC[Photo Vibe Check<br/>FastMCP 2.0<br/>Port 8005]
        VB[Vibe Bit<br/>FastMCP 2.0<br/>Port 8006]
        RSVP[RSVP Service<br/>FastMCP 2.0<br/>Port 8007]
    end
    
    subgraph "Core Services"
        TLT[TLT Service<br/>FastAPI + Agent<br/>Port 8008]
    end
    
    subgraph "Frontend"
        DASH[Next.js Dashboard<br/>Port 3100]
    end
    
    subgraph "External Services"
        DISCORD_API[Discord API]
        OPENAI[OpenAI API]
        REDDIT[Reddit]
    end
    
    subgraph "Storage"
        FS[File System<br/>Guild Data]
        LOGS[Centralized Logs]
    end
    
    DB --> CADDY
    DC --> CADDY
    SC --> CADDY
    CADDY --> DASH
    CADDY --> DA
    CADDY --> SA
    DA --> TLT
    SA --> TLT
    TLT --> GW
    GW --> EM
    GW --> PVC
    GW --> VB
    GW --> RSVP
    TLT -.-> OPENAI
    PVC -.-> REDDIT
    RSVP -.-> OPENAI
    PVC -.-> OPENAI
    VB -.-> OPENAI
    DA -.-> DISCORD_API
    PVC --> FS
    EM --> FS
    VB --> FS
    RSVP --> FS
    GM --> FS
```

## LangGraph Agents

### 1. Ambient Event Agent

The core orchestration agent that manages all event lifecycle operations using LangGraph workflows.

```mermaid
graph TB
    subgraph "Ambient Event Agent LangGraph Workflow"
        INIT[Initialization Node<br/>- Agent startup<br/>- Configuration load<br/>- State initialization]
        
        MONITOR[Event Monitor Node<br/>- Discord events<br/>- Timer events<br/>- CloudEvent processing<br/>- Rate limiting]
        
        REASON[Reasoning Node<br/>- GPT-4o-mini LLM<br/>- Decision making<br/>- Context analysis<br/>- Action planning]
        
        MCP[MCP Executor Node<br/>- Tool execution<br/>- Service calls<br/>- Error handling<br/>- Result processing]
        
        DISCORD[Discord Interface Node<br/>- Message sending<br/>- Embed creation<br/>- Thread management<br/>- Reaction handling]
        
        STATE[(Agent State<br/>- Current context<br/>- Message history<br/>- Active tasks<br/>- Error state)]
    end
    
    INIT --> MONITOR
    MONITOR --> REASON
    REASON --> MCP
    REASON --> DISCORD
    REASON --> MONITOR
    MCP --> MONITOR
    DISCORD --> MONITOR
    
    STATE -.-> INIT
    STATE -.-> MONITOR
    STATE -.-> REASON
    STATE -.-> MCP
    STATE -.-> DISCORD
    
    style INIT fill:#e1f5fe
    style MONITOR fill:#f3e5f5
    style REASON fill:#fff3e0
    style MCP fill:#e8f5e8
    style DISCORD fill:#fce4ec
```

#### Agent State Management

```mermaid
graph LR
    subgraph "AgentState Components"
        MSG["messages: List BaseMessage"]
        TASKS["active_tasks: List AgentTask"]
        CTX["current_context: AgentContext"]
        LOOP["loop_count: int"]
        ERR["error_state: Optional str"]
        TIMER["timer_context: Optional TimerContext"]
        EVENT["event_context: Optional EventContext"]
        DISCORD_CTX["discord_context: Optional DiscordContext"]
        CLOUDEVENT["cloudevent_context: Optional CloudEventContext"]
        DECISION["last_decision: Optional ReasoningDecision"]
        MCP_RESULT["mcp_result: Optional Dict"]
        DISCORD_RESULT["discord_result: Optional Dict"]
        INTERRUPT["interrupt_reason: Optional str"]
    end
    
    MSG --> CTX
    TASKS --> CTX
    CTX --> DECISION
    TIMER --> EVENT
    EVENT --> CLOUDEVENT
    DISCORD_CTX --> CLOUDEVENT
```

### 2. Photo Vibe Check Workflow

AI-powered photo analysis agent using LangGraph for multi-stage photo processing.

```mermaid
graph TB
    subgraph "Photo Vibe Check LangGraph Workflow"
        START([Photo Submission])
        
        DOWNLOAD[Download Photo Node<br/>- URL validation<br/>- Image download<br/>- Format detection<br/>- Size validation]
        
        QUALITY[Check Size Quality Node<br/>- Dimension validation<br/>- File size check<br/>- Format conversion<br/>- Quality assessment]
        
        ANALYZE[Analyze Content Node<br/>- GPT-4o Vision API<br/>- Content analysis<br/>- Vibe assessment<br/>- Scene description]
        
        COMPARE[Compare Similarity Node<br/>- Promotional image comparison<br/>- Semantic similarity<br/>- Context matching<br/>- Event relevance]
        
        SCORE[Calculate Final Score Node<br/>- Weighted scoring<br/>- Confidence calculation<br/>- Result compilation<br/>- Status determination]
        
        END([Processing Complete])
        
        FAIL[Processing Failed]
    end
    
    START --> DOWNLOAD
    DOWNLOAD --> QUALITY
    DOWNLOAD --> FAIL
    QUALITY --> ANALYZE
    QUALITY --> FAIL
    ANALYZE --> COMPARE
    ANALYZE --> FAIL
    COMPARE --> SCORE
    COMPARE --> FAIL
    SCORE --> END
    
    style START fill:#e1f5fe
    style DOWNLOAD fill:#f3e5f5
    style QUALITY fill:#fff3e0
    style ANALYZE fill:#e8f5e8
    style COMPARE fill:#fce4ec
    style SCORE fill:#e0f2f1
    style END fill:#e8f5e8
    style FAIL fill:#ffebee
```

#### Photo Processing State

```mermaid
graph LR
    subgraph "PhotoProcessingWorkflowState"
        PHOTO_URL["photo_url: str"]
        PHOTO_DATA["photo_data: Optional bytes"]
        USER_ID["user_id: str"]
        EVENT_ID["event_id: str"]
        GUILD_ID["guild_id: str"]
        QUALITY["quality_check: Optional Dict"]
        ANALYSIS["content_analysis: Optional Dict"]
        SIMILARITY["similarity_result: Optional Dict"]
        FINAL_SCORE["final_score: Optional float"]
        STATUS["processing_status: str"]
        ERROR["error_message: Optional str"]
    end
    
    PHOTO_URL --> PHOTO_DATA
    PHOTO_DATA --> QUALITY
    QUALITY --> ANALYSIS
    ANALYSIS --> SIMILARITY
    SIMILARITY --> FINAL_SCORE
    ERROR -.-> STATUS
```

## Discord Command Flows

### `/register` Command Flow

```mermaid
flowchart TD
    START([User: /register])
    
    CHECK_ADMIN{Is user admin?}
    ADMIN_ERROR[❌ Error: Admin only]
    
    CHECK_REGISTERED{"Guild already
    registered?"}
    ALREADY_REG["❌ Already registered"]
    
    STORE_GUILD["📝 Store guild in
    local storage"]
    
    CREATE_CLOUDEVENT["☁️ Create CloudEvent
    guild.register"]
    
    SEND_TO_TLT["📤 Send to TLT Service"]
    
    CREATE_EMBED["🎨 Create registration
    embed response"]
    
    SUCCESS[✅ Registration complete]
    
    START --> CHECK_ADMIN
    CHECK_ADMIN -->|No| ADMIN_ERROR
    CHECK_ADMIN -->|Yes| CHECK_REGISTERED
    CHECK_REGISTERED -->|Yes| ALREADY_REG
    CHECK_REGISTERED -->|No| STORE_GUILD
    STORE_GUILD --> CREATE_CLOUDEVENT
    CREATE_CLOUDEVENT --> SEND_TO_TLT
    SEND_TO_TLT --> CREATE_EMBED
    CREATE_EMBED --> SUCCESS
    
    style START fill:#e1f5fe
    style SUCCESS fill:#e8f5e8
    style ADMIN_ERROR fill:#ffebee
    style ALREADY_REG fill:#fff3e0
```

### `/deregister` Command Flow

```mermaid
flowchart TD
    START([User: /deregister])
    
    CHECK_ADMIN{Is user admin?}
    ADMIN_ERROR[❌ Error: Admin only]
    
    CHECK_REGISTERED{Guild registered?}
    NOT_REG[❌ Not registered]
    
    GET_EVENTS[📊 Get active events count]
    GET_REMINDERS[⏰ Get active reminders count]
    
    REMOVE_GUILD["🗑️ Remove guild from
    local storage"]
    
    CREATE_CLOUDEVENT["☁️ Create CloudEvent
    guild.deregister"]
    
    SEND_TO_TLT["📤 Send to TLT Service"]
    
    CREATE_EMBED["🎨 Create deregistration
    embed with impact metrics"]
    
    SUCCESS[✅ Deregistration complete]
    
    START --> CHECK_ADMIN
    CHECK_ADMIN -->|No| ADMIN_ERROR
    CHECK_ADMIN -->|Yes| CHECK_REGISTERED
    CHECK_REGISTERED -->|No| NOT_REG
    CHECK_REGISTERED -->|Yes| GET_EVENTS
    GET_EVENTS --> GET_REMINDERS
    GET_REMINDERS --> REMOVE_GUILD
    REMOVE_GUILD --> CREATE_CLOUDEVENT
    CREATE_CLOUDEVENT --> SEND_TO_TLT
    SEND_TO_TLT --> CREATE_EMBED
    CREATE_EMBED --> SUCCESS
    
    style START fill:#e1f5fe
    style SUCCESS fill:#e8f5e8
    style ADMIN_ERROR fill:#ffebee
    style NOT_REG fill:#fff3e0
```

### `/tlt create` Command Flow

```mermaid
flowchart TD
    START(["User: /tlt create"])
    
    CHECK_REG{"Guild registered?"}
    NOT_REG["❌ Guild not registered"]
    
    SHOW_MODAL["📝 Show Event Create Modal
    - Topic
    - Location
    - Time"]
    
    VALIDATE_INPUT{"Input valid?"}
    INPUT_ERROR["❌ Validation error"]
    
    CREATE_EVENT["🎯 Create event in
    local storage"]
    
    CREATE_EMBED["🎨 Create event embed
    with details"]
    
    POST_MESSAGE["📤 Post event message"]
    
    ADD_REACTIONS["😀 Add default reactions
    ✅ ❌ 🤔 🔥 💯 👀"]
    
    CREATE_PUBLIC_THREAD["🧵 Create public RSVP thread
    (emoji-only rules)"]
    
    CREATE_PRIVATE_THREAD["🔒 Create private planning thread
    (creator only)"]
    
    SCHEDULE_REMINDERS["⏰ Schedule automatic reminders
    24h, 2h, 30min before"]
    
    CREATE_CLOUDEVENT["☁️ Create CloudEvent
    event.created"]
    
    SEND_TO_TLT["📤 Send to TLT Service"]
    
    SUCCESS["✅ Event created successfully"]
    
    START --> CHECK_REG
    CHECK_REG -->|No| NOT_REG
    CHECK_REG -->|Yes| SHOW_MODAL
    SHOW_MODAL --> VALIDATE_INPUT
    VALIDATE_INPUT -->|No| INPUT_ERROR
    VALIDATE_INPUT -->|Yes| CREATE_EVENT
    CREATE_EVENT --> CREATE_EMBED
    CREATE_EMBED --> POST_MESSAGE
    POST_MESSAGE --> ADD_REACTIONS
    ADD_REACTIONS --> CREATE_PUBLIC_THREAD
    CREATE_PUBLIC_THREAD --> CREATE_PRIVATE_THREAD
    CREATE_PRIVATE_THREAD --> SCHEDULE_REMINDERS
    SCHEDULE_REMINDERS --> CREATE_CLOUDEVENT
    CREATE_CLOUDEVENT --> SEND_TO_TLT
    SEND_TO_TLT --> SUCCESS
    
    style START fill:#e1f5fe
    style SUCCESS fill:#e8f5e8
    style NOT_REG fill:#ffebee
    style INPUT_ERROR fill:#ffebee
```

### `/tlt vibe` Command Flow

```mermaid
flowchart TD
    START([User: /tlt vibe])
    
    CHECK_REG{Guild registered?}
    NOT_REG[❌ Guild not registered]
    
    GET_EVENTS[📊 Get guild events]
    
    CHECK_EVENTS{Events exist?}
    NO_EVENTS[❌ No events found]
    
    SHOW_EVENT_SELECT["📝 Show event selection
    dropdown"]
    
    SELECT_EVENT["🎯 User selects event"]
    
    SHOW_ACTION_SELECT["🎨 Show vibe action selection
    📸 Generate Slideshow
    📊 Create Snapshot
    🎨 Canvas Preview
    📷 Photo Summary"]
    
    SELECT_ACTION["⚡ User selects action"]
    
    CREATE_CLOUDEVENT["☁️ Create CloudEvent
    vibe.action.requested"]
    
    SEND_TO_TLT["📤 Send to TLT Service"]
    
    AI_PROCESSING["🤖 AI Agent processes
    vibe request"]
    
    GENERATE_RESULT["🎭 Generate AI content
    - Slideshow
    - Vibe analysis
    - Canvas render
    - Photo summary"]
    
    SEND_RESPONSE[📤 Send result to Discord]
    
    SUCCESS[✅ Vibe action complete]
    
    START --> CHECK_REG
    CHECK_REG -->|No| NOT_REG
    CHECK_REG -->|Yes| GET_EVENTS
    GET_EVENTS --> CHECK_EVENTS
    CHECK_EVENTS -->|No| NO_EVENTS
    CHECK_EVENTS -->|Yes| SHOW_EVENT_SELECT
    SHOW_EVENT_SELECT --> SELECT_EVENT
    SELECT_EVENT --> SHOW_ACTION_SELECT
    SHOW_ACTION_SELECT --> SELECT_ACTION
    SELECT_ACTION --> CREATE_CLOUDEVENT
    CREATE_CLOUDEVENT --> SEND_TO_TLT
    SEND_TO_TLT --> AI_PROCESSING
    AI_PROCESSING --> GENERATE_RESULT
    GENERATE_RESULT --> SEND_RESPONSE
    SEND_RESPONSE --> SUCCESS
    
    style START fill:#e1f5fe
    style SUCCESS fill:#e8f5e8
    style NOT_REG fill:#ffebee
    style NO_EVENTS fill:#fff3e0
    style AI_PROCESSING fill:#f3e5f5
```

## Service Communication Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant D as Discord Adapter
    participant T as TLT Service
    participant A as Ambient Agent
    participant G as MCP Gateway
    participant E as Event Manager
    participant P as Photo Vibe Check
    participant V as Vibe Bit
    participant R as RSVP Service
    
    Note over U,R: Event Creation Flow
    U->>D: /tlt create
    D->>D: Create event locally
    D->>T: CloudEvent: event.created
    T->>A: Process CloudEvent
    A->>A: Reasoning Node
    A->>G: MCP Tool Call
    G->>E: create_event
    E->>E: Store event data
    E-->>G: Event created
    G-->>A: Tool result
    A->>D: Send confirmation
    D->>U: Event created embed
    
    Note over U,R: Photo Submission Flow
    U->>D: DM photo
    D->>T: CloudEvent: photo.submitted
    T->>A: Process CloudEvent
    A->>A: Reasoning Node
    A->>G: MCP Tool Call
    G->>P: submit_photo_dm
    P->>P: LangGraph workflow
    P->>P: AI vibe analysis
    P-->>G: Vibe result
    G-->>A: Tool result
    A->>D: Send vibe response
    D->>U: Vibe check result
    
    Note over U,R: RSVP Flow
    U->>D: React with emoji
    D->>T: CloudEvent: rsvp.submitted
    T->>A: Process CloudEvent
    A->>A: Reasoning Node
    A->>G: MCP Tool Call
    G->>R: create_rsvp
    R->>R: Process RSVP
    R-->>G: RSVP created
    G-->>A: Tool result
    A->>D: Update event stats
```

## Data Flow Architecture

```mermaid
graph TB
    subgraph "State Management"
        ESM["Event State Manager
        tlt/shared/event_state_manager.py"]
        USM["User State Manager
        tlt/shared/user_state_manager.py"]
    end
    
    subgraph "Guild Data Structure"
        GD["guild_data/"]
        DATA["data/"]
        GUILD["guild_id/"]
        EVENT["event_id/"]
        USER["user_id/"]
        
        EVENT_JSON["event.json"]
        USER_JSON["user.json"]
        PHOTOS["photos/"]
        CANVAS["canvas/"]
    end
    
    subgraph "CloudEvent Types"
        CE1["guild.register/deregister"]
        CE2["event.created/updated/deleted"]
        CE3["photo.submitted"]
        CE4["rsvp.submitted/updated"]
        CE5["vibe.action.requested"]
        CE6["timer.reminder"]
    end
    
    ESM --> EVENT_JSON
    USM --> USER_JSON
    
    GD --> DATA
    DATA --> GUILD
    GUILD --> EVENT
    GUILD --> USER
    EVENT --> EVENT_JSON
    EVENT --> PHOTOS
    EVENT --> CANVAS
    USER --> USER_JSON
    
    CE1 -.-> ESM
    CE2 -.-> ESM
    CE3 -.-> ESM
    CE4 -.-> ESM
    CE5 -.-> ESM
    CE6 -.-> ESM
```

## Technology Stack

### Backend Services
- **LangGraph**: Agent orchestration and workflow management
- **FastMCP 2.0**: Model Context Protocol for service communication
- **FastAPI**: REST API framework for adapters and services
- **Discord.py**: Discord bot integration
- **OpenAI GPT-4o**: AI reasoning and photo analysis
- **Pydantic**: Data validation and serialization
- **Loguru**: Structured logging

### Frontend
- **Next.js 15**: Web dashboard framework
- **React 19**: User interface library
- **Tailwind CSS 4**: Styling framework
- **TypeScript**: Type-safe JavaScript

### Infrastructure
- **Docker**: Containerization
- **Caddy**: Reverse proxy and HTTPS termination
- **Supervisord**: Process management
- **Poetry**: Python dependency management
- **Alpine Linux**: Base container OS

### External Integrations
- **Discord API**: Real-time messaging and interactions
- **OpenAI API**: GPT-4o Vision for image analysis
- **CloudEvents**: Standardized event format for service communication

## Security & Reliability

### Authentication & Authorization
- Discord OAuth integration
- Role-based access control (RBAC) via Casbin
- Guild-level permissions
- Admin-only commands

### Rate Limiting
- 30 requests per minute per agent
- Discord API rate limiting compliance
- Photo upload size restrictions
- User action throttling

### Error Handling
- Comprehensive error recovery in LangGraph workflows
- Graceful degradation for service failures
- Retry logic with exponential backoff
- Detailed error logging and monitoring

### Data Persistence
- File system-based state management
- Automatic backup and recovery
- Structured JSON data storage
- Image and media file organization

This architecture provides a scalable, maintainable, and robust platform for Discord-based event management with AI-powered features, built on modern microservices principles and agent-based orchestration.