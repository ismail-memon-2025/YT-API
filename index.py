from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional
from yt_dlp import YoutubeDL
from pytube import YouTube

app = FastAPI(title="YouTube Downloader & Transcriber", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONTACT = "@Ismail_memon"
TG = "https://t.me/jieshuo_india"

def verify_auth(authorization: Optional[str] = Query(None)):
    if (authorization or "").lower() != "ismail":
        raise HTTPException(status_code=401, detail="401: Unauthorized. Please include a valid authorization.")
    return authorization

@app.get("/v1/download")
async def download_video(url: str, quality: Optional[str] = Query(None), authorization: str = Depends(verify_auth)):
    try:
        ydl_opts = {"quiet": True, "skip_download": True, "format": "best"}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            video_list = []
            for f in formats:
                if f.get("vcodec") != "none" and f.get("acodec") != "none" and f.get("url"):
                    if quality:
                        if str(f.get("height")) == quality.replace("p", ""):
                            return {
                                "TG-channel": TG,
                                "creator": CONTACT,
                                "title": info.get("title"),
                                "author": info.get("uploader"),
                                "length": info.get("duration"),
                                "thumbnail_url": info.get("thumbnail"),
                                "download_url": f.get("url"),
                                "format": f.get("ext"),
                                "quality": f.get("format_note")
                            }
                    else:
                        video_list.append({
                            "url": f.get("url"),
                            "format": f.get("ext"),
                            "quality": f.get("format_note") or f.get("height")
                        })
            if quality:
                return JSONResponse(status_code=404, content={
                    "TG-channel": TG,
                    "creator": CONTACT,
                    "error": f"Video not available in {quality} quality."
                })
            return {
                "TG-channel": TG,
                "creator": CONTACT,
                "title": info.get("title"),
                "author": info.get("uploader"),
                "length": info.get("duration"),
                "thumbnail_url": info.get("thumbnail"),
                "available_videos": video_list
            }
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "TG-channel": TG,
            "creator": CONTACT,
            "error": f"Failed to process video. Error: {str(e)}"
        })

@app.get("/v1/transcript")
async def get_transcript(url: str, authorization: str = Depends(verify_auth)):
    try:
        video_id = YouTube(url).video_id
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return {
            "TG-channel": TG,
            "creator": CONTACT,
            "video_id": video_id,
            "transcript": transcript_list
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={
            "TG-channel": TG,
            "creator": CONTACT,
            "error": f"Transcript unavailable. Error: {str(e)}"
        })
