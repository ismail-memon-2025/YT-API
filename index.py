from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional

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
async def download_video(url: str, quality: Optional[str] = Query("720p"), authorization: str = Depends(verify_auth)):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension="mp4", res=quality).first()
        if not stream:
            return JSONResponse(status_code=404, content={
                "TG-channel": TG,
                "creator": CONTACT,
                "error": f"Video not available in {quality} quality."
            })
        return {
            "TG-channel": TG,
            "creator": CONTACT,
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "thumbnail_url": yt.thumbnail_url,
            "download_url": stream.url
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
