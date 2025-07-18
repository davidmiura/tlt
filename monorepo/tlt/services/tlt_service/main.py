"""Main entry point for TLT Service"""

import os
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from loguru import logger


from tlt.services.tlt_service.ambient_event_agent import AmbientEventAgentManager
from tlt.services.tlt_service.monitor import router as monitor_router
from tlt.services.tlt_service.event_manager import router as event_manager_router
from tlt.shared.cloudevents import CloudEvent

# Configure loguru
ENV = os.getenv("ENV", "development").lower()

# Determine log level with priority: LOG_LEVEL env var > ENV-based default
default_log_level = "DEBUG" if ENV == "development" else "INFO"
log_level = os.getenv("LOG_LEVEL", default_log_level).upper()

# Validate log level
valid_log_levels = ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]
if log_level not in valid_log_levels:
    print(f"Warning: Invalid LOG_LEVEL '{log_level}'. Using default '{default_log_level}'")
    log_level = default_log_level

# Remove default handler and add custom ones
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=""),
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    colorize=True
)
logger.add(
    sink="tlt/logs/tlt_service.log",
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    rotation="1 day",
    retention="30 days",
    compression="gz"
)

# Log the configured log level
logger.info(f"TLT Service logging configured: ENV={ENV}, LOG_LEVEL={log_level}")

# Environment configuration
ENV_FILE = f".env.{ENV}"

# Load environment variables based on stage
env_path = Path(__file__).parent.parent.parent / ENV_FILE
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded environment from {ENV_FILE}")
else:
    logger.warning(f"Environment file {ENV_FILE} not found, using default .env")
    load_dotenv()

# Global agent manager instance
agent_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    global agent_manager
    
    # Startup
    logger.info(f"Starting TLT Service in {ENV} environment")
    
    # Initialize agent manager
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.warning(f"OPENAI_API_KEY not found in environment variables for {ENV} environment")
        logger.warning("Agent functionality will be limited without API key")
        agent_manager = None
    else:
        try:
            agent_manager = AmbientEventAgentManager(
                openai_api_key=openai_api_key,
                debug_mode=(ENV == "development")
            )
            
            # Start the agent manager
            await agent_manager.start()
            logger.debug("TLT Service with ambient agent started successfully")
            
            # Set the agent manager in the CloudEvents router
            set_agent_manager(agent_manager)
        except Exception as e:
            logger.error(f"Failed to start ambient agent: {e}")
            logger.warning("Continuing without ambient agent functionality")
            agent_manager = None
    
    # Set the agent manager in the CloudEvents router (even if None)
    set_agent_manager(agent_manager)
    
    yield
    
    # Shutdown
    logger.info("Shutting down TLT Service")
    if agent_manager:
        await agent_manager.stop()
    logger.info("TLT Service shutdown complete")

# Initialize FastAPI app
app = FastAPI(
    title=f"TLT Service ({ENV})",
    description="Event management service with ambient agent integration",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(monitor_router, prefix="/monitor", tags=["monitoring"])
# app.include_router(event_manager_router, prefix="/events", tags=["event_manager"])

# CloudEvents router
from tlt.services.tlt_service.cloudevents_router import router as cloudevents_router, set_agent_manager
app.include_router(cloudevents_router, tags=["cloudevents"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    global agent_manager
    agent_status = "unknown"
    
    if agent_manager:
        agent_status = await agent_manager.get_status()
    
    return {
        "status": "healthy",
        "environment": ENV,
        "agent_status": agent_status,
        "timestamp": "2025-07-02T00:00:00Z"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "TLT Service",
        "version": "1.0.0",
        "environment": ENV,
        "endpoints": {
            "health": "/health",
            "monitor": "/monitor",
            "events": "/events",
            "cloudevents": "/cloudevents"
        }
    }


def main():
    """Main entry point for TLT Service"""
    port = int(os.getenv('PORT', 8008))
    logger.info(f"Starting TLT Service on port {port}")
    
    uvicorn.run(
        "tlt.services.tlt_service.main:app",
        host="0.0.0.0",
        port=port,
        reload=(ENV == "development"),
        log_level="debug" if ENV == "development" else "info"
    )

if __name__ == "__main__":
    main()