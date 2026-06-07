import os
import tempfile
import yt_dlp
from faster_whisper import WhisperModel


_whisper = WhisperModel("base", device="cpu", compute_type="int8")


def get_instagram_metadata(reel_url: str) -> dict:
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(reel_url, download=False)

    description = info.get("description", "") or ""
    hashtags = [word for word in description.split() if word.startswith("#")]

    return {
        "title": description[:100],
        "creator": info.get("uploader"),
        "follower_count": None,
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
        "comments": info.get("comment_count"),
        "upload_date": info.get("upload_date"),
        "duration_seconds": info.get("duration"),
        "hashtags": hashtags,
    }


def get_instagram_transcript(reel_url: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(tmpdir, "audio.%(ext)s"),
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([reel_url])

        audio_file = next(f for f in os.listdir(tmpdir) if f.startswith("audio"))
        audio_path = os.path.join(tmpdir, audio_file)

        segments, _ = _whisper.transcribe(audio_path, beam_size=5)
        return " ".join(seg.text for seg in segments)