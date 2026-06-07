from services.supabase_client import get_supabase
from services.embeddings import embed_query


def search_chunks(session_id: str, query: str, top_k: int = 5) -> list[dict]:
    sb = get_supabase()
    query_embedding = embed_query(query)

    result = sb.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "session_id_filter": session_id,
        "match_count": top_k,
    }).execute()

    return result.data


def get_session_metadata(session_id: str) -> list[dict]:
    sb = get_supabase()
    result = sb.table("video_metadata").select("*").eq("session_id", session_id).execute()
    return result.data