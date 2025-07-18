import os
import sys
from pathlib import Path
from loguru import logger
from fastmcp import FastMCP

# Add the current directory to sys.path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from tlt.mcp_services.vibe_bit.service import VibeBitService
from tlt.mcp_services.vibe_bit.canvas_renderer import CanvasRenderer
from tlt.mcp_services.vibe_bit.tools import register_tools
from tlt.mcp_services.vibe_bit.resources import register_resources

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
    sink="tlt/logs/vibe_bit.log",
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    rotation="1 day",
    retention="30 days",
    compression="gz"
)

# Initialize FastMCP server
mcp = FastMCP("TLT Vibe Bit")

# Initialize services
event_manager_url = os.getenv('EVENT_MANAGER_URL', 'http://localhost:8004')

service = VibeBitService(event_manager_url=event_manager_url)
renderer = CanvasRenderer()

# Register tools and resources
register_tools(mcp, service, renderer)
register_resources(mcp, service, renderer)

def main():
    """Main entry point for FastMCP Vibe Bit server"""
    # Get port from environment or default to 8006
    port = int(os.getenv('PORT', 8006))
    
    # Run the MCP server
    # Default to streamable-http transport for production readiness
    # Can be overridden with MCP_TRANSPORT environment variable
    transport = os.getenv('MCP_TRANSPORT', 'streamable-http')
    
    if transport == 'stdio':
        logger.info("Starting TLT Vibe Bit with stdio transport")
        mcp.run()
    else:
        logger.info(f"Starting TLT Vibe Bit with {transport} transport on port {port}")
        mcp.run(transport=transport, port=port)

if __name__ == "__main__":
    main()
