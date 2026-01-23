from fastapi import APIRouter, HTTPException, Query
import requests
from typing import Optional
from config import get_settings
from logger import setup_logger

router = APIRouter(prefix="/external", tags=["integrations"])
settings = get_settings()
logger = setup_logger("integrations")

# Reusable HTTP session
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": settings.user_agent})


def _get_json(url: str, params: dict, timeout: Optional[float] = None):
    """Helper for external API calls with robust error handling"""
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
    """Current weather data from Open-Meteo API"""
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
    """Hourly and daily weather forecast from Open-Meteo API"""
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

    # Format hourly data
    hours = []
    for i, time in enumerate(hourly.get("time", [])):
        hours.append({
            "time": time,
            "temp": hourly.get("temperature_2m", [None])[i],
            "pop": hourly.get("precipitation_probability", [None])[i],
            "code": hourly.get("weathercode", [None])[i],
        })

    # Format daily data
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
    """Reverse geocoding using BigDataCloud API (free and reliable)"""
    url = "https://api.bigdatacloud.net/data/reverse-geocode-client"
    params = {
        "latitude": lat,
        "longitude": lon,
        "localityLanguage": "fr"
    }

    try:
        data = _get_json(url, params, timeout=5.0)

        city = data.get("city") or data.get("locality") or data.get("principalSubdivision")
        state = data.get("principalSubdivision")
        country = data.get("countryName")
        country_code = (data.get("countryCode") or "").upper()

        parts = [p for p in [city, country] if p]
        label = ", ".join(parts)

        logger.info(f"Geocoded ({lat}, {lon}) -> {label}")
        return {
            "city": city,
            "state": state,
            "country": country,
            "country_code": country_code,
            "label": label
        }
    except Exception as e:
        # Fallback: return coordinates as label
        logger.warning(f"Geocoding failed, using fallback: {e}")
        return {
            "city": None,
            "state": None,
            "country": None,
            "country_code": None,
            "label": f"{lat:.2f}, {lon:.2f}"
        }