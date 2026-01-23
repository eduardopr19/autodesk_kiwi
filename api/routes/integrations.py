from fastapi import APIRouter, HTTPException, Query
import requests
from typing import Optional
from config import get_settings
from logger import setup_logger

router = APIRouter(prefix="/external", tags=["integrations"])
settings = get_settings()
logger = setup_logger("integrations")

# Session HTTP réutilisable
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": settings.user_agent})


def _get_json(url: str, params: dict, timeout: Optional[float] = None):
    """Helper pour appels API externes avec gestion d'erreurs robuste"""
    try:
        response = SESSION.get(
            url,
            params=params,
            timeout=timeout or settings.api_timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"Timeout calling {url}")
        raise HTTPException(status_code=504, detail="External API timeout - please try again later")
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error calling {url}")
        raise HTTPException(status_code=503, detail="External API unreachable - service may be down")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error calling {url}: {e.response.status_code}")
        raise HTTPException(status_code=502, detail="External API returned an error")
    except requests.exceptions.RequestException as e:
        logger.error(f"Unexpected error calling {url}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch external data")


@router.get("/weather")
def weather(lat: float = Query(...), lon: float = Query(...)):
    """Météo actuelle (Open-Meteo)"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "windspeed_unit": "kmh",
        "timezone": "auto",
    }
    data = _get_json(url, params)
    
    current = data.get("current_weather", {})
    logger.info(f"Weather fetched for ({lat}, {lon})")
    return {
        "temp": current.get("temperature"),
        "windspeed": current.get("windspeed"),
        "winddirection": current.get("winddirection"),
        "weathercode": current.get("weathercode"),
        "is_day": current.get("is_day"),
        "time": current.get("time")
    }


@router.get("/forecast")
def forecast(lat: float = Query(...), lon: float = Query(...)):
    """Prévisions horaires + journalières"""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,precipitation_probability,weathercode",
        "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "windspeed_unit": "kmh",
        "timezone": "auto",
    }
    data = _get_json(url, params)

    hourly = data.get("hourly", {})
    daily = data.get("daily", {})

    # Format horaire
    hours = []
    for i, time in enumerate(hourly.get("time", [])):
        hours.append({
            "time": time,
            "temp": hourly.get("temperature_2m", [None])[i],
            "pop": hourly.get("precipitation_probability", [None])[i],
            "code": hourly.get("weathercode", [None])[i],
        })

    # Format journalier
    days = []
    for i, date in enumerate(daily.get("time", [])):
        days.append({
            "date": date,
            "tmin": daily.get("temperature_2m_min", [None])[i],
            "tmax": daily.get("temperature_2m_max", [None])[i],
            "pop": daily.get("precipitation_probability_max", [None])[i],
            "code": daily.get("weathercode", [None])[i],
        })

    logger.info(f"Forecast fetched: {len(hours)} hours, {len(days)} days")
    return {"hourly": hours, "daily": days}


@router.get("/reverse-geocode")
def reverse_geocode(lat: float = Query(...), lon: float = Query(...)):
    """Géocodage inverse (Nominatim)"""
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "format": "jsonv2",
        "lat": lat,
        "lon": lon,
        "zoom": 10,
        "addressdetails": 1,
    }
    data = _get_json(url, params)

    address = data.get("address", {})
    city = (
        address.get("city") or
        address.get("town") or
        address.get("village") or
        address.get("municipality")
    )
    state = address.get("state")
    country = address.get("country")
    country_code = (address.get("country_code") or "").upper()

    parts = [p for p in [city, state, country] if p]
    label = ", ".join(parts) or data.get("display_name", "")

    logger.info(f"Geocoded ({lat}, {lon}) -> {label}")
    return {
        "city": city,
        "state": state,
        "country": country,
        "country_code": country_code,
        "label": label
    }