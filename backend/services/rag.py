import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from services.retrieval import search_chunks, get_session_metadata
from services.supabase_client import get_supabase

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    streaming=True,
    google_api_key=os.environ["GOOGLE_API_KEY"],
)

SYSTEM_PROMPT = """You are a social media analytics assistant for creators.
You have access to transcript chunks and metadata from two videos (Video A and Video B).
Answer questions using ONLY the provided context. Always cite your sources.
Citation format: [Video A, chunk N] or [Video B, metadata]

CONTEXT:
{context}

METADATA:
{metadata}
"""


def build_context(session_id: str, question: str) -> tuple[str, str, list]:
    chunks = search_chunks(session_id, question, top_k=6)
    metadata = get_session_metadata(session_id)

    context = "\n\n".join([
        f"[Video {c['video_id']}, chunk {c['chunk_index']}]: {c['content']}"
        for c in chunks
    ])

    metadata_str = "\n".join([
        f"Video {m['video_id']} ({m['platform']}): "
        f"creator={m['creator']}, views={m['views']}, likes={m['likes']}, "
        f"comments={m['comments']}, engagement_rate={m['engagement_rate']}%, "
        f"followers={m['follower_count']}, hashtags={m['hashtags']}"
        for m in metadata
    ])

    citations = [
        {
            "video_id": c["video_id"],
            "chunk_index": c["chunk_index"],
            "content_snippet": c["content"][:100],
        }
        for c in chunks
    ]

    return context, metadata_str, citations


def build_messages(system_prompt: str, history: list, question: str) -> list:
    messages = [SystemMessage(content=system_prompt)]
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            messages.append(AIMessage(content=msg["content"]))
    messages.append(HumanMessage(content=question))
    return messages


def get_chat_history(chat_id: str) -> list[dict]:
    sb = get_supabase()
    result = (
        sb.table("messages")
        .select("role, content")
        .eq("chat_id", chat_id)
        .order("created_at")
        .execute()
    )
    return result.data