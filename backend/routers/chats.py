from fastapi import APIRouter
from services.supabase_client import get_supabase

router = APIRouter()


@router.get("/")
def list_chats(user_id: str):
    sb = get_supabase()
    result = (
        sb.table("chats")
        .select("id, title, created_at, updated_at, session_id")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data


@router.get("/{chat_id}/messages")
def get_messages(chat_id: str):
    sb = get_supabase()
    result = (
        sb.table("messages")
        .select("id, role, content, citations, created_at")
        .eq("chat_id", chat_id)
        .order("created_at")
        .execute()
    )
    return result.data


@router.get("/{chat_id}/session")
def get_session(chat_id: str):
    sb = get_supabase()
    chat = sb.table("chats").select("session_id").eq("id", chat_id).single().execute()
    meta = (
        sb.table("video_metadata")
        .select("*")
        .eq("session_id", chat.data["session_id"])
        .execute()
    )
    return {"session_id": chat.data["session_id"], "metadata": meta.data}


@router.delete("/{chat_id}")
def delete_chat(chat_id: str):
    sb = get_supabase()
    sb.table("chats").delete().eq("id", chat_id).execute()
    return {"deleted": chat_id}