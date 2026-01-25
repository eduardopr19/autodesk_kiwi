import base64
import os
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

load_dotenv()

router = APIRouter(prefix="/spotify", tags=["Spotify"])

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8000/spotify/callback")

SPOTIFY_SCOPES = "user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-recently-played"

_tokens = {
    "access_token": None,
    "refresh_token": None,
    "expires_at": None
}


class SpotifyTrack(BaseModel):
    is_playing: bool = False
    track_name: str | None = None
    artist_name: str | None = None
    album_name: str | None = None
    album_art: str | None = None
    progress_ms: int | None = None
    duration_ms: int | None = None
    track_url: str | None = None
    error: str = ""


class SpotifyStatus(BaseModel):
    connected: bool = False
    error: str = ""


def _get_auth_header():
    credentials = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    return base64.b64encode(credentials.encode()).decode()


def _is_token_valid():
    if not _tokens["access_token"] or not _tokens["expires_at"]:
        return False
    return datetime.now() < _tokens["expires_at"]


def _refresh_access_token():
    if not _tokens["refresh_token"]:
        return False

    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {_get_auth_header()}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "refresh_token",
                "refresh_token": _tokens["refresh_token"]
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            _tokens["access_token"] = data["access_token"]
            _tokens["expires_at"] = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
            if "refresh_token" in data:
                _tokens["refresh_token"] = data["refresh_token"]
            return True
        return False
    except Exception as e:
        print(f"Token refresh error: {e}")
        return False


def _get_valid_token():
    if _is_token_valid():
        return _tokens["access_token"]

    if _refresh_access_token():
        return _tokens["access_token"]

    return None


def _spotify_api_request(endpoint: str, method: str = "GET", data: dict = None):
    token = _get_valid_token()
    if not token:
        return None, "Not authenticated with Spotify"

    url = f"https://api.spotify.com/v1{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=10)
        else:
            return None, f"Unknown method: {method}"

        if response.status_code == 204:
            return {}, None
        elif response.status_code == 200:
            return response.json(), None
        elif response.status_code == 401:
            if _refresh_access_token():
                return _spotify_api_request(endpoint, method, data)
            return None, "Authentication expired"
        else:
            return None, f"Spotify API error: {response.status_code}"
    except Exception as e:
        return None, f"Request error: {str(e)}"


@router.get("/login")
def spotify_login():
    if not SPOTIFY_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Spotify Client ID not configured")

    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={SPOTIFY_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope={SPOTIFY_SCOPES.replace(' ', '%20')}"
    )
    return RedirectResponse(url=auth_url)


@router.get("/callback")
def spotify_callback(code: str = Query(None), error: str = Query(None)):
    if error:
        return RedirectResponse(url="/?spotify_error=" + error)

    if not code:
        return RedirectResponse(url="/?spotify_error=no_code")

    try:
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {_get_auth_header()}",
                "Content-Type": "application/x-www-form-urlencoded"
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": SPOTIFY_REDIRECT_URI
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            _tokens["access_token"] = data["access_token"]
            _tokens["refresh_token"] = data["refresh_token"]
            _tokens["expires_at"] = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
            return RedirectResponse(url="/?spotify_connected=true")
        else:
            return RedirectResponse(url="/?spotify_error=token_exchange_failed")

    except Exception as e:
        print(f"Spotify callback error: {e}")
        return RedirectResponse(url="/?spotify_error=exception")


@router.get("/status", response_model=SpotifyStatus)
def spotify_status():
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return SpotifyStatus(connected=False, error="Spotify not configured in .env")

    token = _get_valid_token()
    return SpotifyStatus(connected=token is not None)


@router.post("/logout")
def spotify_logout():
    _tokens["access_token"] = None
    _tokens["refresh_token"] = None
    _tokens["expires_at"] = None
    return {"success": True, "message": "Logged out from Spotify"}


@router.get("/now-playing", response_model=SpotifyTrack)
def get_now_playing():
    data, error = _spotify_api_request("/me/player/currently-playing")

    if error:
        return SpotifyTrack(error=error)

    if not data or not data.get("item"):
        return SpotifyTrack(is_playing=False, error="Nothing playing")

    item = data["item"]
    artists = ", ".join([a["name"] for a in item.get("artists", [])])

    album_art = None
    images = item.get("album", {}).get("images", [])
    if images:
        album_art = images[1]["url"] if len(images) > 1 else images[0]["url"]

    return SpotifyTrack(
        is_playing=data.get("is_playing", False),
        track_name=item.get("name"),
        artist_name=artists,
        album_name=item.get("album", {}).get("name"),
        album_art=album_art,
        progress_ms=data.get("progress_ms"),
        duration_ms=item.get("duration_ms"),
        track_url=item.get("external_urls", {}).get("spotify")
    )


@router.post("/play")
def play():
    _, error = _spotify_api_request("/me/player/play", method="PUT")
    if error:
        return {"success": False, "error": error}
    return {"success": True}


@router.post("/pause")
def pause():
    _, error = _spotify_api_request("/me/player/pause", method="PUT")
    if error:
        return {"success": False, "error": error}
    return {"success": True}


@router.post("/next")
def next_track():
    _, error = _spotify_api_request("/me/player/next", method="POST")
    if error:
        return {"success": False, "error": error}
    return {"success": True}


@router.post("/previous")
def previous_track():
    _, error = _spotify_api_request("/me/player/previous", method="POST")
    if error:
        return {"success": False, "error": error}
    return {"success": True}


@router.get("/recent")
def get_recent_tracks(limit: int = 5):
    data, error = _spotify_api_request(f"/me/player/recently-played?limit={limit}")

    if error:
        return {"tracks": [], "error": error}

    tracks = []
    for item in data.get("items", []):
        track = item.get("track", {})
        artists = ", ".join([a["name"] for a in track.get("artists", [])])

        album_art = None
        images = track.get("album", {}).get("images", [])
        if images:
            album_art = images[-1]["url"]

        tracks.append({
            "name": track.get("name"),
            "artist": artists,
            "album_art": album_art,
            "played_at": item.get("played_at")
        })

    return {"tracks": tracks}
