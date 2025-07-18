# tlt/adapters/discord_adapter/health.py
import sys
try:
    print("OK")
except Exception as e:
    print("FAILED:", e)
    sys.exit(1)

from fastapi import APIRouter, HTTPException
import requests
import logging
from tlt.adapters.discord_adapter.bot_manager import bot

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "bot_status": "online" if bot.is_ready() else "offline"
    }

@router.get("/ping")
async def ping():
    """Simple ping endpoint for load balancers and monitoring"""
    return {"pong": True}
