import random
from datetime import datetime, timezone

import requests
from fastapi import APIRouter

from config import get_settings
from logger import setup_logger

router = APIRouter(prefix="/meta", tags=["meta"])
settings = get_settings()
logger = setup_logger("meta")

FALLBACK_QUOTES = [
    {"content": "Focus on progress, not perfection.", "author": "Unknown"},
    {"content": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
    {"content": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
    {"content": "Done is better than perfect.", "author": "Sheryl Sandberg"},
    {"content": "Small steps lead to big changes.", "author": "Unknown"},
]

def fetch_random_quote():
    try:
        response = requests.get(
            "https://api.quotable.io/random",
            params={"maxLength": 150},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        return {
            "content": data["content"],
            "author": data["author"]
        }
    except Exception as e:
        logger.warning(f"Failed to fetch quote from API: {e}")
        return random.choice(FALLBACK_QUOTES)


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.app_version,
        "app": settings.app_name,
    }


@router.get("/overview")
def overview():
    quote = fetch_random_quote()
    return {
        "quote": quote["content"],
        "quote_author": quote["author"]
    }


@router.get("/quote")
def get_quote():
    return fetch_random_quote()
