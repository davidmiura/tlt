import os
import logging
import uvicorn
from fastapi import FastAPI
from pathlib import Path
from dotenv import load_dotenv
import threading

try:
    # Try absolute imports first (preferred)
    from tlt.adapters.discord_adapter.bot_manager import DiscordBot
    from tlt.adapters.discord_adapter.health import router as health_router
    from tlt.adapters.discord_adapter.event import router as event_router
    from tlt.adapters.discord_adapter.rsvp import router as rsvp_router
    from tlt.adapters.discord_adapter.reminder import router as reminder_router
    from tlt.adapters.discord_adapter.experience_manager import router as experience_router
except ImportError:
    # Fall back to local imports (when run directly)
    from bot_manager import DiscordBot
    from health import router as health_router
    from event import router as event_router
    from rsvp import router as rsvp_router
    from reminder import router as reminder_router
    from experience_manager import router as experience_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tlt/logs/discord_adapter.log')
    ]
)
logger = logging.getLogger(__name__)

# Environment configuration
ENV = os.getenv("ENV", "development").lower()
ENV_FILE = f".env.{ENV}"

# Load environment variables based on stage
env_path = Path(__file__).parent.parent.parent / ENV_FILE
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded environment from {ENV_FILE}")
else:
    logger.warning(f"Environment file {ENV_FILE} not found, using default .env")
    load_dotenv()

# Initialize FastAPI app
app = FastAPI(title=f"Discord Adapter ({ENV})")

# Include routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(event_router, prefix="/events", tags=["events"])
app.include_router(rsvp_router, prefix="/rsvp", tags=["rsvp"])
app.include_router(reminder_router, prefix="/reminders", tags=["reminders"])
app.include_router(experience_router, prefix="/experience", tags=["experience"])

# Initialize Discord bot
bot = DiscordBot()

def run_bot():
    """Run the Discord bot"""
    try:
        token = os.getenv('DISCORD_TOKEN')
        if not token:
            raise ValueError(f"No Discord token found in environment variables for {ENV} environment")
        
        logger.info("Starting Discord bot...")
        # Run bot with appropriate log level for environment
        log_level = logging.DEBUG if ENV == "development" else logging.DEBUG
        bot.run(token, log_level=log_level)
        
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")
        raise

def run_api():
    """Run the FastAPI server"""
    port = int(os.getenv('PORT', 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

def main():
    """Main entry point for Discord Adapter"""
    try:
        logger.info(f"Starting Discord Adapter in {ENV} mode on port {os.getenv('PORT', 8001)}")
        
        # Start the bot in a separate thread
        bot_thread = threading.Thread(target=run_bot, name="DiscordBot", daemon=False)
        bot_thread.start()
        
        # Give the bot thread a moment to start
        import time
        time.sleep(2)
        
        # Check if bot thread started successfully
        if not bot_thread.is_alive():
            logger.error("Discord bot thread failed to start")
            return
        
        logger.info("Discord bot thread started successfully")
        
        # Run the FastAPI server in the main thread
        logger.info("Starting FastAPI server...")
        run_api()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Failed to start Discord Adapter: {e}")
        raise

if __name__ == "__main__":
    main()
