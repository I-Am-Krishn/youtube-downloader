from fastapi import FastAPI, HTTPException, Query
from typing import Dict, Any, List
import yt_dlp
import time

app = FastAPI(
    title="YouTube Intelligence API",
    version="3.2",
    description="""
🚀 YouTube Intelligence API (Flag-Based)

• Best-resolution download included by default
• Optional heavy data via flags
• Playlist support (opt-in)
• No fake permanent links

Creator: Krishn Dhola
"""
)

# -----------------------
# Cache (metadata only)
# -----------------------
CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 900  # 15 minutes


# -----------------------
# Helpers
# -----------------------
def is_youtube_url(url: str) -> bool:
    return any(x in url for x in [
        "youtube.com/watch",
        "youtube.com/shorts",
        "youtu.be/",
        "youtube.com/playlist"
    ])


def pick_best_progressive(progressive: dict):
    best = None
    for items in progressive.values():
        for f in items:
            if f.get("ext") == "mp4":
                if not best or (f.get("height", 0) > best.get("height", 0)):
                    best = f
    return best


def extract_single(url: str) -> Dict[str, Any]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    progressive = {}
    audio_only = {}

    for f in info.get("formats", []):
        if f.get("vcodec") != "none" and f.get("acodec") != "none":
            progressive.setdefault(f.get("resolution"), []).append(f)
        elif f.get("acodec") != "none":
            audio_only.setdefault(f.get("abr"), []).append(f)

    return {
        "video": {
            "title": info.get("title"),
            "description": info.get("description"),
            "tags": info.get("tags") or [],
            "thumbnail": info.get("thumbnail"),
            "type": "shorts" if info.get("duration", 0) <= 60 else "video",
        },
        "streams": progressive,
        "chapters": info.get("chapters") or [],
        "subtitles": {
            "manual": info.get("subtitles") or {},
            "auto": info.get("automatic_captions") or {}
        },
        "stats": {
            "views": info.get("view_count"),
            "likes": info.get("like_count"),
            "comments": info.get("comment_count"),
        },
        "creator": {
            "channel": info.get("uploader"),
            "channel_url": info.get("uploader_url"),
            "subscribers": info.get("channel_follower_count"),
        }
    }


def extract_playlist(url: str) -> Dict[str, Any]:
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    videos = []
    for entry in info.get("entries", []):
        videos.append({
            "title": entry.get("title"),
            "url": entry.get("url")
        })

    return {
        "title": info.get("title"),
        "count": len(videos),
        "videos": videos
    }


# -----------------------
# Route
# -----------------------
@app.get("/api/youtube")
def youtube_api(
    url: str = Query(...),
    downloads: bool = False,
    subtitles: bool = False,
    chapters: bool = False,
    stats: bool = False,
    creator: bool = False,
    playlist: bool = False,
):
    if not is_youtube_url(url):
        raise HTTPException(400, "Only YouTube URLs are supported")

    # -----------------------
    # Playlist mode
    # -----------------------
    if playlist:
        playlist_data = extract_playlist(url)
        return {
            "playlist": {
                "title": playlist_data["title"],
                "count": playlist_data["count"]
            },
            "videos": playlist_data["videos"],
            "credits": {"creator": "Krishn Dhola"},
            "_options": {
                "playlist": "Use &playlist=true (already enabled)",
                "note": "Per-video details require individual video requests"
            }
        }

    # -----------------------
    # Single video mode
    # -----------------------
    data = extract_single(url)
    best = pick_best_progressive(data["streams"])

    response = {
        "title": data["video"]["title"],
        "description": data["video"]["description"],
        "tags": data["video"]["tags"],
        "type": data["video"]["type"],
        "thumbnail": data["video"]["thumbnail"],

        "download": {
            "quality": best.get("resolution") if best else None,
            "ext": best.get("ext") if best else None,
            "stream_url": best.get("url") if best else None
        },

        "credits": {"creator": "Krishn Dhola"},

        "_options": {
            "downloads": "Use &downloads=true to get all resolutions",
            "subtitles": "Use &subtitles=true to get English subtitles",
            "chapters": "Use &chapters=true to include chapters",
            "stats": "Use &stats=true to include views & likes",
            "creator": "Use &creator=true to include channel info",
            "playlist": "Use &playlist=true to process entire playlist (heavy)"
        }
    }

    if downloads:
        response["downloads"] = data["streams"]

    if subtitles:
        response["subtitles"] = {
            "en": {
                "manual": [t["url"] for t in data["subtitles"]["manual"].get("en", [])],
                "auto": [t["url"] for t in data["subtitles"]["auto"].get("en", [])]
            }
        }

    if chapters:
        response["chapters"] = data["chapters"]

    if stats:
        response["stats"] = data["stats"]

    if creator:
        response["creator"] = data["creator"]

    return response
