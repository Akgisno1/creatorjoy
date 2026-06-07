from fastapi import APIRouter,HTTPException
from models.schemas import IngestRequest, IngestResponse, VideoMetadataOut
from services.supabase_client import get_supabase
from services.youtube import (
    get_youtube_transcript,
    get_youtube_metadata,
    compute_engagement_rate,
)
from services.instagram import get_instagram_metadata, get_instagram_transcript

router=APIRouter()

@router.post("/",response_model=IngestResponse)
async def ingest_video(req:IngestRequest):
    sb = get_supabase()

    session = sb.table("video_sessions").insert({
        "video_a_url": req.video_a_url,
        "video_b_url": req.video_b_url,
        "user_id": req.user_id,
    }).execute()
    session_id = session.data[0]["id"]

    try:
        meta_a = get_youtube_metadata(req.video_a_url)
        transcript_a = get_youtube_transcript(req.video_a_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"YouTube fetch failed: {str(e)}")

    meta_a["engagement_rate"] = compute_engagement_rate(
        meta_a["views"], meta_a["likes"], meta_a["comments"]
    )

    try:
        meta_b = get_instagram_metadata(req.video_b_url)
        transcript_b = get_instagram_transcript(req.video_b_url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Instagram fetch failed: {str(e)}")

    meta_b["engagement_rate"] = compute_engagement_rate(
        meta_b["views"], meta_b["likes"], meta_b["comments"]
    )

    for video_id, platform, url, meta in [
        ("A", "youtube", req.video_a_url, meta_a),
        ("B", "instagram", req.video_b_url, meta_b),
    ]:
        sb.table("video_metadata").insert({
            "session_id": session_id,
            "video_id": video_id,
            "platform": platform,
            "url": url,
            **meta,
        }).execute()

    # Step 05: uncomment after creating backend/services/embeddings.py
    # from services.embeddings import chunk_and_embed
    # await chunk_and_embed(session_id, "A", transcript_a)
    # await chunk_and_embed(session_id, "B", transcript_b)

    chat = sb.table("chats").insert({
        "session_id": session_id,
        "user_id": req.user_id,
        "title": f"{meta_a.get('title', 'Video A')[:50]} vs {meta_b.get('title', 'Video B')[:50]}",
    }).execute()
    chat_id = chat.data[0]["id"]

    return IngestResponse(
        session_id=session_id,
        chat_id=chat_id,
        video_a=VideoMetadataOut(video_id="A", platform="youtube", **meta_a),
        video_b=VideoMetadataOut(video_id="B", platform="instagram", **meta_b),
    )