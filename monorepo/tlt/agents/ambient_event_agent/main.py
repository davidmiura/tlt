"""Main entry point for ambient event agent"""

import os
import sys
import asyncio
import argparse
import signal
from datetime import datetime, timezone
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from tlt.agents.ambient_event_agent.agent.agent import AmbientEventAgent

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
    sink="tlt/logs/ambient_event_agent.log",
    format="{time:YYYY-MM-DD HH:mm:ss,SSS} - {name} - {level} - {message}",
    level=log_level,
    rotation="1 day",
    retention="30 days",
    compression="gz"
)

# Log the configured log level
logger.debug(f"Ambient Event Agent logging configured: ENV={ENV}, LOG_LEVEL={log_level}")

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

class AmbientAgentProcess:
    """Process manager for the ambient event agent"""
    
    def __init__(self):
        self.agent: Optional[AmbientEventAgent] = None
        self.running = False
        self.shutdown_event = asyncio.Event()
    
    async def start(self, config: dict):
        """Start the ambient agent process"""
        try:
            logger.info("Starting Ambient Event Agent Process")
            
            # Validate configuration
            openai_api_key = config.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError(f"OPENAI_API_KEY is required in environment variables for {ENV} environment")
            
            logger.info(f"OpenAI API key loaded from environment (key starts with: {openai_api_key[:8]}...)")
            
            # Create agent
            agent_id = config.get("agent_id", f"ambient_agent_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
            debug_mode = config.get("debug_mode", ENV == "development")
            
            self.agent = AmbientEventAgent(
                openai_api_key=openai_api_key,
                agent_id=agent_id,
                debug_mode=debug_mode,
                config=config
            )
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Initialize agent
            logger.info("Initializing agent...")
            await self.agent.initialize()
            
            self.running = True
            logger.info(f"Agent {agent_id} started successfully in {ENV} environment")
            
            # Run continuous operation
            max_iterations = config.get("max_iterations")
            sleep_interval = config.get("sleep_interval", 5.0)
            
            await self._run_with_monitoring(max_iterations, sleep_interval)
            
        except Exception as e:
            logger.error(f"Failed to start agent: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _run_with_monitoring(self, max_iterations: Optional[int], sleep_interval: float):
        """Run agent with health monitoring"""
        last_health_check = datetime.now(timezone.utc)
        health_check_interval = 300  # 5 minutes
        
        try:
            # Create tasks for agent and monitoring
            agent_task = asyncio.create_task(
                self.agent.run_continuous(max_iterations, sleep_interval)
            )
            
            shutdown_task = asyncio.create_task(self.shutdown_event.wait())
            
            # Wait for either completion or shutdown
            done, pending = await asyncio.wait(
                [agent_task, shutdown_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel pending tasks
            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            
            # Check if agent task completed normally or with error
            if agent_task in done:
                try:
                    await agent_task
                    logger.info("Agent completed normally")
                except Exception as e:
                    logger.error(f"Agent completed with error: {e}")
                    raise
            else:
                logger.info("Agent shutdown requested")
        
        except asyncio.CancelledError:
            logger.info("Agent operation cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in agent monitoring: {e}")
            raise
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def shutdown(self):
        """Initiate graceful shutdown"""
        logger.info("Initiating graceful shutdown")
        self.running = False
        
        if self.agent:
            await self.agent.stop()
        
        self.shutdown_event.set()
    
    async def _cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up agent resources")
        
        if self.agent:
            # Log final metrics
            metrics = self.agent.get_metrics()
            logger.info(f"Final agent metrics: {metrics}")
        
        self.running = False

def create_config_from_args(args) -> dict:
    """Create configuration from command line arguments"""
    config = {
        "agent_id": args.agent_id,
        "debug_mode": args.debug,
        "max_iterations": args.max_iterations,
        "sleep_interval": args.sleep_interval,
        "recursion_limit": 1000,  # Increased recursion limit for LangGraph
        "max_retry_attempts": 3,
        "enable_loop_detection": True
    }
    
    return config

async def generate_mermaid_diagram():
    """Generate and save Mermaid diagram of the agent graph"""
    try:
        logger.info("Generating LangGraph Mermaid diagram...")
        
        # Create a minimal agent instance just for diagram generation
        dummy_api_key = "dummy-key-for-diagram"
        config = {
            "recursion_limit": 500,
            "max_retry_attempts": 3
        }
        
        agent = AmbientEventAgent(
            openai_api_key=dummy_api_key,
            agent_id="diagram_agent",
            debug_mode=True,
            config=config
        )
        
        # Generate the Mermaid diagram
        try:
            # Try to get the mermaid representation
            mermaid_code = agent.graph.get_graph().draw_mermaid()
            
            # Save to file
            output_file = "ambient_event_agent_graph.mmd"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(mermaid_code)
            
            logger.info(f"✅ Mermaid diagram saved to: {output_file}")
            print(f"\n📊 Graph diagram generated successfully!")
            print(f"📄 File: {output_file}")
            print(f"🌐 View online: https://mermaid.live/")
            print(f"\nMermaid Code:")
            print("-" * 50)
            print(mermaid_code)
            print("-" * 50)
            
        except AttributeError:
            # Fallback: try alternative method
            try:
                mermaid_code = agent.graph.get_graph().draw_mermaid_png()
                output_file = "ambient_event_agent_graph.mmd"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(str(mermaid_code))
                logger.info(f"✅ Mermaid diagram (alternative) saved to: {output_file}")
            except Exception as e:
                logger.warning(f"Could not generate Mermaid with built-in methods: {e}")
                # Manual diagram generation
                mermaid_code = generate_manual_mermaid_diagram()
                output_file = "ambient_event_agent_graph.mmd"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(mermaid_code)
                logger.info(f"✅ Manual Mermaid diagram saved to: {output_file}")
                print(f"\n📊 Graph diagram generated successfully (manual)!")
                print(f"📄 File: {output_file}")
                print(f"🌐 View online: https://mermaid.live/")
        
    except Exception as e:
        logger.error(f"Failed to generate diagram: {e}")
        # Create a basic manual diagram as fallback
        mermaid_code = generate_manual_mermaid_diagram()
        output_file = "ambient_event_agent_graph.mmd"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        logger.info(f"✅ Fallback Mermaid diagram saved to: {output_file}")

def generate_manual_mermaid_diagram() -> str:
    """Generate a manual Mermaid diagram based on the known graph structure"""
    return """graph TD
    Start([Start]) --> Init[initialization]
    Init --> InitCheck{Initialization OK?}
    InitCheck -->|Success| Monitor[event_monitor]
    InitCheck -->|Error| End([End])
    
    Monitor --> MonitorCheck{Continue Monitoring?}
    MonitorCheck -->|Has Events| Reasoning[reasoning]
    MonitorCheck -->|No Events & Debug| End
    MonitorCheck -->|No Events & Continue| Monitor
    MonitorCheck -->|Stopping| End
    MonitorCheck -->|Error & Retry| Monitor
    MonitorCheck -->|Error & Max Retries| End
    
    Reasoning --> ActionCheck{Execute Actions?}
    ActionCheck -->|MCP Needed| MCP[mcp_executor]
    ActionCheck -->|Discord Needed| Discord[discord_interface]
    ActionCheck -->|No Actions| Monitor
    
    MCP --> MCPCheck{After MCP?}
    MCPCheck -->|Has Messages| Discord
    MCPCheck -->|No Messages| Monitor
    
    Discord --> DiscordCheck{After Discord?}
    DiscordCheck -->|Continue| Monitor
    DiscordCheck -->|Stopping| End
    
    style Start fill:#e1f5fe
    style End fill:#ffebee
    style Init fill:#f3e5f5
    style Monitor fill:#e8f5e8
    style Reasoning fill:#fff3e0
    style MCP fill:#fce4ec
    style Discord fill:#e3f2fd
    
    classDef decision fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    class InitCheck,MonitorCheck,ActionCheck,MCPCheck,DiscordCheck decision
"""

async def main():
    """Main entry point"""
    logger.info(f"Starting Ambient Event Agent in {ENV} mode")
    parser = argparse.ArgumentParser(
        description="Ambient Event Agent",
        epilog="Examples:\n"
               "  %(prog)s --debug                     # Run in debug mode\n"
               "  %(prog)s --generate-diagram          # Generate graph diagram and exit\n"
               "  ENV=production %(prog)s              # Run in production mode\n"
               "  %(prog)s --max-iterations 10         # Run for 10 iterations then stop",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--agent-id",
        type=str,
        help="Unique agent identifier"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        help="Maximum number of processing cycles (default: unlimited)"
    )
    
    parser.add_argument(
        "--sleep-interval",
        type=float,
        default=5.0,
        help="Sleep interval between cycles in seconds (default: 5.0)"
    )
    
    parser.add_argument(
        "--config-file",
        type=str,
        help="Path to configuration file (JSON)"
    )
    
    parser.add_argument(
        "--generate-diagram",
        action="store_true",
        help="Generate Mermaid diagram of the agent graph and exit"
    )
    
    args = parser.parse_args()
    
    # Handle diagram generation request
    if args.generate_diagram:
        await generate_mermaid_diagram()
        return 0
    
    # Create configuration
    config = create_config_from_args(args)
    
    # Load config file if specified
    if args.config_file:
        import json
        try:
            with open(args.config_file, 'r') as f:
                file_config = json.load(f)
                config.update(file_config)
        except Exception as e:
            logger.error(f"Failed to load config file {args.config_file}: {e}")
            return 1
    
    # Create and start process
    process = AmbientAgentProcess()
    
    try:
        await process.start(config)
        return 0
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        return 0
    except Exception as e:
        logger.error(f"Agent process failed: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        sys.exit(1)