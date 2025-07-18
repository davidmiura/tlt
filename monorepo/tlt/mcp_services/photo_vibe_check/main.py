import os
from dotenv import load_dotenv
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.photo_vibe_check.service import PhotoVibeCheckService
from tlt.mcp_services.photo_vibe_check.photo_processor import PhotoProcessor
from tlt.mcp_services.photo_vibe_check.tools import register_tools
from tlt.mcp_services.photo_vibe_check.resources import register_resources

# Load environment variables from .env files
load_dotenv()  # Load .env
load_dotenv(f".env.{os.getenv('ENV', 'development')}")  # Load environment-specific .env

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
    sink="tlt/logs/photo_vibe_check.log",
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    rotation="1 day",
    retention="30 days",
    compression="gz"
)

# Initialize FastMCP server
mcp = FastMCP("TLT Photo Vibe Check")

# Initialize services
event_manager_url = os.getenv('EVENT_MANAGER_URL', 'http://localhost:8004')
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    logger.warning("OPENAI_API_KEY not set. Photo analysis will be disabled.")
    openai_api_key = "dummy-key-for-testing"  # Allow server to start without real key

service = PhotoVibeCheckService(event_manager_url=event_manager_url)
processor = PhotoProcessor(openai_api_key=openai_api_key)

# Register tools and resources
register_tools(mcp, service, processor)
register_resources(mcp, service)

def main():
    """Main entry point for FastMCP Photo Vibe Check server"""
    # Get port from environment or default to 8005
    port = int(os.getenv('PORT', 8005))
    
    # Run the MCP server
    # Default to streamable-http transport for production readiness
    # Can be overridden with MCP_TRANSPORT environment variable
    transport = os.getenv('MCP_TRANSPORT', 'streamable-http')
    
    if transport == 'stdio':
        logger.info("Starting TLT Photo Vibe Check with stdio transport")
        mcp.run()
    else:
        logger.info(f"Starting TLT Photo Vibe Check with {transport} transport on port {port}")
        mcp.run(transport=transport, port=port)

if __name__ == "__main__":
    main()
