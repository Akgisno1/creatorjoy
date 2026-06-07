import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url: str) -> str:
    """Pull video ID from common YouTube URL formats."""
    patterns = [
        r"(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract YouTube video ID from: {url}")


def get_youtube_transcript(video_url: str) -> str:
    video_id = extract_video_id(video_url)
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join(t["text"] for t in transcript_list)


def get_youtube_metadata(video_url: str) -> dict:
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

    return {
        "title": info.get("title"),
        "creator": info.get("uploader"),
        "follower_count": info.get("channel_follower_count"),
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
        "comments": info.get("comment_count"),
        "upload_date": info.get("upload_date"),
        "duration_seconds": info.get("duration"),
        "hashtags": [],
    }


def compute_engagement_rate(views, likes, comments) -> float:
    if not views or views == 0:
        return 0.0
    return round(((likes or 0) + (comments or 0)) / views * 100, 4)