import os
import sys
from loguru import logger
from dotenv import load_dotenv
from pathlib import Path
from fastmcp import FastMCP
from tlt.mcp_services.rsvp.service import RSVPService
from tlt.mcp_services.rsvp.tools import register_tools
from tlt.mcp_services.rsvp.resources import register_resources

# Configure loguru
ENV = os.getenv("ENV", "development").lower()

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


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
    sink="tlt/logs/rsvp_service.log",
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    rotation="1 day",
    retention="30 days",
    compression="gz"
)

# Log the configured log level
logger.debug(f"MCP RSVP logging configured: ENV={ENV}, LOG_LEVEL={log_level}")

# Environment configuration
ENV_FILE = f".env.{ENV}"

# Load environment variables based on stage
env_path = Path(project_root) / ENV_FILE
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded environment from {ENV_FILE}")
else:
    logger.warning(f"Environment file {ENV_FILE} not found, using default .env")
    load_dotenv()


# Initialize FastMCP server
mcp = FastMCP("TLT RSVP Service")

# Initialize service
rsvp_service = RSVPService()

# Register tools and resources
register_tools(mcp, rsvp_service)
register_resources(mcp, rsvp_service)

def main():
    """Main entry point for FastMCP RSVP server"""
    
    # Add custom route to handle /mcp without redirect
    try:
        from fastapi.responses import RedirectResponse
        
        @mcp.app.get("/mcp")
        async def mcp_redirect_fix():
            """Handle /mcp requests without 307 redirect"""
            return RedirectResponse(url="/mcp/", status_code=301)
            
        logger.info("Added MCP redirect fix for /mcp endpoint")
    except Exception as e:
        logger.warning(f"Could not add redirect fix: {e}")
    
    # Get port from environment or default to 8007
    port = int(os.getenv('PORT', 8007))
    
    # Run the MCP server
    # Default to streamable-http transport for production readiness
    # Can be overridden with MCP_TRANSPORT environment variable
    transport = os.getenv('MCP_TRANSPORT', 'streamable-http')
    
    if transport == 'stdio':
        logger.info("Starting TLT RSVP Service with stdio transport")
        mcp.run()
    else:
        logger.info(f"Starting TLT RSVP Service with {transport} transport on port {port}")
        mcp.run(transport=transport, port=port)

if __name__ == "__main__":
    main()