import os
from loguru import logger
from fastmcp import FastMCP
from tlt.mcp_services.guild_manager.service import GuildManagerService
from tlt.mcp_services.guild_manager.tools import register_tools
from tlt.mcp_services.guild_manager.resources import register_resources

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
    sink="tlt/logs/guild_manager.log",
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    rotation="1 day",
    retention="30 days",
    compression="gz"
)

# Create FastMCP instance
mcp = FastMCP("Guild Manager")

# Create service instance
service = GuildManagerService()

# Register tools and resources
register_tools(mcp, service)
register_resources(mcp, service)

def main():
    """Main entry point for FastMCP Guild Manager server"""
    # Get port from environment or default to 8009
    port = int(os.getenv('PORT', 8009))
    
    # Run the MCP server
    # Default to streamable-http transport for production readiness
    # Can be overridden with MCP_TRANSPORT environment variable
    transport = os.getenv('MCP_TRANSPORT', 'streamable-http')
    
    if transport == 'stdio':
        logger.info("Starting TLT Guild Manager with stdio transport")
        mcp.run()
    else:
        logger.info(f"Starting TLT Guild Manager with {transport} transport on port {port}")
        mcp.run(transport=transport, port=port)

if __name__ == "__main__":
    main()