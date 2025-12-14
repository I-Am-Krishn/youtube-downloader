from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
import yt_dlp
import time

app = FastAPI(
    title="YouTube Intelligence API",
    version="4.1",
    description="Direct-link YouTube downloader API | Creator: Krishn Dhola"
)

# ---------------- RATE LIMIT ----------------
RATE_LIMIT = 200
WINDOW = 3600
rate_store = {}

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host
    now = time.time()

    rec = rate_store.get(ip, {"count": 0, "start": now})
    if now - rec["start"] > WINDOW:
        rec = {"count": 0, "start": now}

    rec["count"] += 1
    rate_store[ip] = rec

    if rec["count"] > RATE_LIMIT:
        return JSONResponse(status_code=429, content={"error": "Rate limit exceeded"})

    return await call_next(request)

# ---------------- HELPERS ----------------
def extract_info(url, flat=False):
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": flat,
        "noplaylist": not flat,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        return ydl.extract_info(url, download=False)

def best_video(info):
    best = None
    for f in info.get("formats", []):
        if f.get("vcodec") != "none" and f.get("acodec") != "none":
            if not best or (f.get("height", 0) > best.get("height", 0)):
                best = f
    return best

# ---------------- API ----------------
@app.get("/api/youtube/download")
def download(url: str = Query(...)):
    info = extract_info(url)
    best = best_video(info)
    if not best:
        raise HTTPException(400, "No stream found")

    # SAME behavior you already like
    return RedirectResponse(best["url"], status_code=302)

@app.get("/api/youtube/playlist")
def playlist(url: str = Query(...)):
    info = extract_info(url, flat=True)
    entries = info.get("entries", [])[:10]

    videos = []
    for v in entries:
        vurl = f"https://youtu.be/{v['id']}"
        videos.append({
            "title": v.get("title"),
            "link": vurl,
            "download": f"/api/youtube/download?url={vurl}"
        })

    return {
        "playlist": {
            "title": info.get("title"),
            "returned": len(videos),
            "limit": 10
        },
        "videos": videos
    }

# ---------------- UI ----------------
@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
<!DOCTYPE html>
<html>
<head>
<title>YouTube Downloader</title>
<style>
body{background:#111;color:#fff;font-family:Arial}
.box{max-width:600px;margin:40px auto}
input,button{width:100%;padding:12px;margin:8px 0}
button{background:#e11;color:#fff;border:none}
.card{background:#1c1c1c;padding:10px;margin:10px 0}
a{color:#4af}
small{opacity:.7}
</style>
</head>
<body>
<div class="box">
<h2>YouTube Downloader</h2>
<input id="url" placeholder="Paste YouTube video or playlist URL">
<button onclick="go()">Get Download</button>
<div id="out"></div>
</div>

<script>
async function go(){
  const url = document.getElementById('url').value;
  const out = document.getElementById('out');
  out.innerHTML = 'Loading...';

  try {
    const r = await fetch('/api/youtube/playlist?url='+encodeURIComponent(url));
    const d = await r.json();

    out.innerHTML = '<h3>'+d.playlist.title+'</h3>';
    d.videos.forEach(v=>{
      out.innerHTML += `
      <div class="card">
        <b>${v.title}</b><br>
        <a href="${v.download}" target="_blank">Download</a><br>
        <small>Opens video. Use browser download option.</small>
      </div>`;
    });
  } catch {
    out.innerHTML = `
      <div class="card">
        <a href="/api/youtube/download?url=${encodeURIComponent(url)}" target="_blank">
          Download
        </a><br>
        <small>Opens video. Use browser download option.</small>
      </div>`;
  }
}
</script>
</body>
</html>
"""
