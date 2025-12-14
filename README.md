# 🎬 YouTube Downloader & Intelligence API

A **self-hosted YouTube Downloader API** built with **FastAPI + yt-dlp**.

Paste a YouTube link → get a **direct video stream link** → download using your browser.

No ads.  
No tracking.  
No extensions.  
No fake promises.

> ⚠️ This is **source-code only**.  
> You run it on **your own server**.

---

## ✨ Features

- ✅ Direct video download endpoint (no proxy)
- ✅ Playlist support (hard-limited to 10 videos)
- ✅ Downloader-style Web UI
- ✅ Rate limiting (200 requests/hour/IP)
- ✅ Graceful handling of YouTube bot checks
- ✅ Clean JSON responses
- ✅ Beginner-friendly, developer-friendly

---

## 🚫 What This Project Does NOT Do

This project is intentionally honest:

- ❌ No forced downloads without proxying
- ❌ No cookie stealing
- ❌ No login bypass
- ❌ No private or age-restricted video hacks
- ❌ No “unlimited scraping forever”

If YouTube blocks a request, the API tells you.  
It does **not** crash or lie.

---

## 🔗 Source Code    
> `https://github.com/I-Am-Krishn/youtube-downloader/`

---

## 🧠 How It Works (In Simple Terms)

- The server **does not download videos**
- It **extracts the best available stream**
- It **redirects the user’s browser** to that stream
- The user downloads using normal browser controls

✔ Uses YouTube’s bandwidth  
✔ Uses the user’s bandwidth  
✔ Your server stays lightweight  

---

## 🚀 API Endpoints

### 1️⃣ Download a Single Video

```

GET /api/youtube/download?url=YOUTUBE_VIDEO_URL

```

**What happens:**
- Redirects to the best available video stream
- Video opens in a new tab
- User downloads via browser menu or right-click

**Example:**
```

/api/youtube/download?url=[https://youtu.be/VIDEO_ID](https://youtu.be/VIDEO_ID)

```

---

### 2️⃣ Playlist Support (Max 10 Videos)

```

GET /api/youtube/playlist?url=YOUTUBE_PLAYLIST_URL

````

**Rules:**
- Hard limit: **10 videos**
- Limit cannot be overridden
- Designed to prevent abuse

**Example response:**
```json
{
  "playlist": {
    "title": "Playlist Name",
    "returned": 10,
    "limit": 10
  },
  "videos": [
    {
      "title": "Video Title",
      "link": "https://youtu.be/VIDEO_ID",
      "download": "/api/youtube/download?url=https://youtu.be/VIDEO_ID"
    }
  ]
}
````

---

### 3️⃣ Web UI (Downloader-Style)

```
GET /ui
```

**What the UI does:**

* Paste a YouTube video or playlist URL
* Click **Get Download**
* Click **Download**
* Video opens in a new tab
* Download using browser controls

No API knowledge required.

---

## ⏱️ Rate Limiting

* **200 requests per hour per IP**
* No API keys
* Transparent behavior
* Protects your server IP reputation

When exceeded:

```json
{
  "error": "Rate limit exceeded"
}
```

---

## 🤖 YouTube Bot Checks (Important)

Sometimes YouTube responds with:

> “Sign in to confirm you’re not a bot”

When this happens:

* The API returns a clean error
* No server crash
* No fake data

Example response:

```json
{
  "detail": "YouTube blocked this request (bot verification). Try again later."
}
```

This depends on:

* Server IP reputation
* Traffic patterns
* YouTube’s internal systems

No downloader can fully avoid this.

---

## 🛠️ Installation & Setup

### Requirements

* Python **3.10+**
* Linux server or VPS recommended

### Install dependencies

```bash
pip install fastapi uvicorn yt-dlp
```

### Run locally

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Access

* API docs: `http://localhost:8000/docs`
* UI: `http://localhost:8000/ui`

---

## 🐳 Docker (Optional)

If you’re deploying with Docker / EasyPanel:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install fastapi uvicorn yt-dlp

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📌 Use Cases

* Personal archiving
* Educational content backup
* Developer tools
* Internal automation
* Clean alternative to ad-filled downloader sites

---

## 🧩 Possible Extensions

* Audio-only endpoint
* Resolution selector (720p / 1080p)
* Optional proxy support
* Cookie-based auth (user-provided)
* ZIP packaging (proxy-based)

---

## 👤 Credits

**Created by:** Krishn Dhola

---

## 🧾 License

Choose a license that fits your goals (MIT recommended).

---

## Final Note

This project exists because most “YouTube downloaders” online are:

* Bloated
* Dishonest
* Unsafe

This one is:

* Simple
* Transparent
* Self-hosted

Use it responsibly.
