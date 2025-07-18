#!/usr/bin/env python3
"""
Test main.py for MCP Gateway without RBAC complexity
"""

import os
import sys
from loguru import logger

from tlt.mcp_services.gateway.gateway_simple_test import SimpleTestGateway

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

# Initialize gateway
gateway = SimpleTestGateway()
mcp = gateway.get_mcp_instance()

def main():
    """Main entry point for FastMCP Gateway test version"""
    logger.info("Starting TLT MCP Gateway - Test Version")
    
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