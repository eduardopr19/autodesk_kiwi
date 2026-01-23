from fastapi import APIRouter
from datetime import datetime, timezone
from config import get_settings

router = APIRouter(prefix="/meta", tags=["meta"])
settings = get_settings()


@router.get("/health")
def health():
    """Health check with system info"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.app_version,
        "app": settings.app_name,
    }


@router.get("/overview")
def overview():
    """Daily summary - mockup for MVP"""
    return {
        "quote": "Focus on progress, not perfection.",
        "next_event": {
            "title": "Cours Réseau",
            "time": "08:30",
            "room": "B204"
        },
        "weather": {
            "temp": 16,
            "condition": "Couvert"
        },
        "unread": {
            "proton": 0
        }
    }