import os
import sys
from loguru import logger

from tlt.mcp_services.gateway.gateway_simple import SimpleGateway
from tlt.mcp_services.gateway.resources import register_resources

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
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    colorize=True
)
logger.add(
    sink="tlt/logs/mcp_gateway.log",
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    rotation="1 day",
    retention="30 days",
    compression="gz"
)

# Initialize gateway with proxies and RBAC
gateway = SimpleGateway()
mcp = gateway.get_mcp_instance()

# Register resources
register_resources(mcp, gateway)

def main():
    """Main entry point for FastMCP Gateway with proxy support"""
    logger.info("Starting TLT MCP Gateway with proxy and RBAC support")
    
    # Note: FastMCP 2.0 handles routing automatically
    logger.info("Gateway initialized with FastMCP 2.0")
    
    # Get port from environment or default to 8003
    port = int(os.getenv('PORT', 8003))
    
    # Run the MCP server
    # Default to streamable-http transport for production readiness
    # Can be overridden with MCP_TRANSPORT environment variable
    transport = os.getenv('MCP_TRANSPORT', 'streamable-http')
    
    if transport == 'stdio':
        logger.info("Starting TLT MCP Gateway with stdio transport")
        mcp.run()
    else:
        logger.info(f"Starting TLT MCP Gateway with {transport} transport on port {port}")
        mcp.run(transport=transport, port=port)

if __name__ == "__main__":
    main()